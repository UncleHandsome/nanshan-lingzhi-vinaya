# -*- coding: utf-8 -*-
"""六書 3K 材料多輪校對 orchestrator。

設定：qwk2 金鑰、50 workers、qwen4-max-preview、xhigh、enable_search＋search_strategy=max。
流程：
  第 1–3 輪：全量 3K 材料校對；每輪結束套用修正、重產材料；每輪結果完整保留。
  第 4–5 輪：只抽「最近一輪仍有問題」的 key（前幾輪有問題但後來已 NONE 者不再抽）。
每輪輸出：六書_3K_校對_20261124/round{N}/材料/ 與 /輸出/。
配額耗盡或 STOP → 優雅停止，保留已完成結果。

用法：
  python -X utf8 _src/run_3k_review.py            # 從 state 接續
  python -X utf8 _src/run_3k_review.py --smoke    # 只測 1 檔 1 worker
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

sys.path.insert(0, os.path.dirname(__file__))
import make_3k_plain as M

B = M.B
ROOT = os.path.join(B, '六書_3K_校對_20261124')
KEY_FILE = os.path.join(B, 'qwk2.txt')
BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = os.environ.get('QWEN_MODEL', 'qwen4-max-preview')
MAX_TOKENS = int(os.environ.get('QWEN_MAX_TOKENS', '32768'))
WORKERS = 50
ROUNDS = 5
QUOTA = threading.Event()
STOP_REASON = ''
HAN = re.compile(r'[\u4e00-\u9fff]')


def log(msg):
    line = '[%s] %s' % (time.strftime('%m-%d %H:%M:%S'), msg)
    print(line, flush=True)
    with io.open(os.path.join(ROOT, 'run.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def stop_flag():
    return os.path.join(ROOT, 'STOP')


def load_state():
    p = os.path.join(ROOT, 'state.json')
    if os.path.exists(p):
        return json.load(io.open(p, encoding='utf-8'))
    return {'rounds_done': [], 'keys': {}}


def save_state(st):
    io.open(os.path.join(ROOT, 'state.json'), 'w', encoding='utf-8').write(
        json.dumps(st, ensure_ascii=False, indent=1))


def all_segment_keys():
    """回傳 {key_id: (book, rowkey, si)}；key_id = book|material_key。"""
    out = {}
    for book_id, _, label in M.BOOKS:
        for ln in io.open(os.path.join(B, '定稿', book_id + '.jsonl'), encoding='utf-8'):
            if not ln.strip():
                continue
            r = json.loads(ln)
            segs = r.get('segments') or []
            for si, s in enumerate(segs, 1):
                mk = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
                out['%s|%s' % (book_id, mk)] = (book_id, str(r['key']), si, label, s)
    return out


def gen_materials(outdir, keymap, target=None):
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    idx = 0
    filekeys = {}
    for book_id, _, label in M.BOOKS:
        buf = []
        size = 0
        curkeys = []

        def flush():
            nonlocal buf, size, idx, curkeys
            if not buf:
                return
            idx += 1
            name = '%04d_%s.md' % (idx, book_id)
            body = M.PROMPT.format(book_id=book_id) + '\n\n' + '\n'.join(buf)
            io.open(os.path.join(outdir, name), 'w', encoding='utf-8', newline='\n').write(body)
            filekeys[name] = curkeys
            buf = []
            size = 0
            curkeys = []
        for kid, (bid, rowkey, si, lab, s) in keymap.items():
            if bid != book_id:
                continue
            if target is not None and kid not in target:
                continue
            mk = kid.split('|', 1)[1]
            b = M.block(book_id, label, mk, s)
            n = len(b.encode('utf-8')) + 1
            if buf and size + n > 3000:
                flush()
            buf.append(b)
            size += n
            curkeys.append(kid)
        flush()
    io.open(os.path.join(outdir, '_filekeys.json'), 'w', encoding='utf-8').write(
        json.dumps(filekeys, ensure_ascii=False))
    return idx


def call_qwen(text, key):
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': text}],
        'enable_thinking': True,
        'reasoning_effort': 'xhigh',
        'enable_search': True,
        'search_options': {'search_strategy': 'max'},
        'max_completion_tokens': MAX_TOKENS,
    }
    req = urllib.request.Request(
        BASE + '/chat/completions', data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
        method='POST')
    with urllib.request.urlopen(req, timeout=1800) as r:
        obj = json.loads(r.read().decode('utf-8'))
    return (obj.get('choices') or [{}])[0].get('message', {}).get('content') or ''


def valid(out):
    s = out.strip()
    if s.upper().rstrip('.。') == 'NONE':
        return True
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            return False
        if 'translation' not in o or 'key' not in o:
            return False
    return True


def run_one(src, outdir, key):
    global STOP_REASON
    stem = os.path.basename(src)[:-3]
    dst = os.path.join(outdir, stem + '_回.txt')
    marker = os.path.join(outdir, stem + '.done')
    if os.path.exists(marker) and os.path.exists(dst):
        return 'skip'
    if QUOTA.is_set() or os.path.exists(stop_flag()):
        return 'stopped'
    text = io.open(src, encoding='utf-8').read()
    last = ''
    for attempt in range(3):
        if QUOTA.is_set() or os.path.exists(stop_flag()):
            return 'stopped'
        try:
            out = call_qwen(text, key).strip()
            if not out:
                last = 'empty'
                time.sleep(5 * (attempt + 1))
                continue
            if not valid(out):
                last = 'invalid-shape'
                time.sleep(5 * (attempt + 1))
                continue
            io.open(dst, 'w', encoding='utf-8', newline='\n').write(out + '\n')
            io.open(marker, 'w', encoding='utf-8').write('ok\n')
            return 'ok'
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:400]
            last = 'HTTP%d %s' % (e.code, body[:80])
            low = body.lower()
            if e.code in (401, 402) or 'insufficient_quota' in low or ('quota' in low and e.code in (403, 429)):
                QUOTA.set()
                STOP_REASON = last
                return 'quota'
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(15 * (attempt + 1))
                continue
            break
        except Exception as e:
            last = type(e).__name__ + ': ' + str(e)[:100]
            if attempt < 2:
                time.sleep(8 * (attempt + 1))
                continue
            break
    return 'fail ' + last


def run_batch(matdir, outdir, workers):
    os.makedirs(outdir, exist_ok=True)
    key = io.open(KEY_FILE, encoding='utf-8-sig').read().strip()
    files = sorted(p for p in glob.glob(os.path.join(matdir, '*.md')))
    todo = [p for p in files if not (os.path.exists(os.path.join(outdir, os.path.basename(p)[:-3] + '.done'))
                                    and os.path.exists(os.path.join(outdir, os.path.basename(p)[:-3] + '_回.txt')))]
    log('batch 待跑 %d／%d workers=%d' % (len(todo), len(files), workers))
    ok = fail = skip = 0
    it = iter(todo)
    inflight = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for p in it:
            inflight[ex.submit(run_one, p, outdir, key)] = p
            if len(inflight) >= workers:
                break
        while inflight:
            ds, _ = wait(inflight, return_when=FIRST_COMPLETED)
            for f in ds:
                p = inflight.pop(f)
                try:
                    st = f.result()
                except Exception as e:
                    st = 'err ' + str(e)[:60]
                if st == 'ok':
                    ok += 1
                elif st == 'skip':
                    skip += 1
                else:
                    fail += 1
                    if st != 'stopped':
                        log('%s %s' % (os.path.basename(p), st))
                if (ok + fail) % 50 == 0:
                    log('ok=%d fail=%d inflight=%d' % (ok, fail, len(inflight)))
            if QUOTA.is_set() or os.path.exists(stop_flag()):
                continue
            while len(inflight) < workers:
                try:
                    p = next(it)
                except StopIteration:
                    break
                inflight[ex.submit(run_one, p, outdir, key)] = p
    log('batch 結束 ok=%d fail=%d skip=%d' % (ok, fail, skip))
    return ok, fail


def parse_round(outdir, filekeys):
    """回傳 {key_id: ('FIX', translation) 或 ('NONE', None)}。"""
    res = {}
    for name, kids in filekeys.items():
        rp = os.path.join(outdir, name[:-3] + '_回.txt')
        if not os.path.exists(rp):
            continue
        text = io.open(rp, encoding='utf-8').read().strip()
        fixmap = {}
        if text and text.upper().rstrip('.。') != 'NONE':
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                k = str(o.get('key') or '')
                if '／' in k:
                    k = k.rsplit('／', 1)[-1]
                if '/' in k:
                    k = k.rsplit('/', 1)[-1]
                tr = (o.get('translation') or '').strip()
                if k and tr:
                    fixmap[k] = tr
        for kid in kids:
            bid, mk = kid.split('|', 1)
            if mk in fixmap:
                res[kid] = ('FIX', fixmap[mk])
            else:
                res[kid] = ('NONE', None)
    return res


def apply_fixes(results, keymap, round_no):
    bybook = {}
    for kid, (st, tr) in results.items():
        if st != 'FIX':
            continue
        bid, rowkey, si, lab, s = keymap[kid]
        bybook.setdefault(bid, []).append((rowkey, si, tr))
    applied = 0
    for bid, fixes in bybook.items():
        path = os.path.join(B, '定稿', bid + '.jsonl')
        bak = os.path.join(B, '定稿', '_舊_%s_before_review_r%d_20261124.jsonl' % (bid, round_no))
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        bykey = {str(r['key']): r for r in rows}
        for rowkey, si, tr in fixes:
            r = bykey.get(rowkey)
            if not r:
                continue
            segs = r.get('segments') or []
            if 1 <= si <= len(segs):
                segs[si - 1]['translation'] = tr
                r['translation'] = '\n\n'.join((s.get('translation') or '') for s in segs)
                applied += 1
        io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
            json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    return applied


def latest_fix_keys(st):
    out = set()
    for kid, hist in st['keys'].items():
        if hist and hist[-1]['status'] == 'FIX':
            out.add(kid)
    return out


def do_round(r, st, workers):
    rdir = os.path.join(ROOT, 'round%d' % r)
    matdir = os.path.join(rdir, '材料')
    outdir = os.path.join(rdir, '輸出')
    keymap = all_segment_keys()
    if r <= 3:
        target = None
    else:
        target = latest_fix_keys(st)
        if not target:
            log('round%d 無待復校 key，跳過' % r)
            st['rounds_done'].append(r)
            save_state(st)
            return True
    n = gen_materials(matdir, keymap, target)
    log('round%d 材料 %d 檔（target=%s）' % (r, n, '全量' if target is None else len(target)))
    run_batch(matdir, outdir, workers)
    filekeys = json.load(io.open(os.path.join(matdir, '_filekeys.json'), encoding='utf-8'))
    results = parse_round(outdir, filekeys)
    applied = apply_fixes(results, keymap, r)
    fixn = sum(1 for v in results.values() if v[0] == 'FIX')
    for kid, (stt, tr) in results.items():
        st['keys'].setdefault(kid, []).append({'round': r, 'status': stt})
    st['rounds_done'].append(r)
    save_state(st)
    log('round%d 完成：有問題 %d、套用 %d、累計 key %d' % (r, fixn, applied, len(st['keys'])))
    io.open(os.path.join(rdir, 'summary.json'), 'w', encoding='utf-8').write(
        json.dumps({'round': r, 'files': n, 'fix': fixn, 'applied': applied,
                    'results': {k: v[0] for k, v in results.items()}}, ensure_ascii=False, indent=1))
    return not QUOTA.is_set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--workers', type=int, default=WORKERS)
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    if a.smoke:
        keymap = all_segment_keys()
        matdir = os.path.join(ROOT, 'smoke', '材料')
        outdir = os.path.join(ROOT, 'smoke', '輸出')
        first = next(iter(keymap))
        gen_materials(matdir, keymap, {first})
        run_batch(matdir, outdir, 1)
        for p in glob.glob(os.path.join(outdir, '*_回.txt')):
            log('SMOKE %s -> %s' % (os.path.basename(p), io.open(p, encoding='utf-8').read()[:120]))
        return
    st = load_state()
    for r in range(1, ROUNDS + 1):
        if r in st['rounds_done']:
            log('round%d 已完成，跳過' % r)
            continue
        if os.path.exists(stop_flag()):
            log('STOP 存在，停止')
            break
        cont = do_round(r, st, a.workers)
        if not cont:
            log('配額耗盡／停止，保留結果，退出。reason=%s' % STOP_REASON)
            break
    log('orchestrator 結束 rounds_done=%s' % st['rounds_done'])


if __name__ == '__main__':
    main()
