# -*- coding: utf-8 -*-
"""六書 3K 材料多輪校對 orchestrator（Token Plan / Responses API 版）。

設定：
  - qwk2 金鑰（sk-sp-）、50 workers、qwen4-max、reasoning=xhigh
  - Responses API（/responses）+ web_search（可選 web_extractor）+ stream=True
流程：
  - 第 1–3 輪：全量 3K 材料校對；每輪完成後套用 fixed 修正、重產材料；完整保留每輪報告與輸出。
  - 第 4–5 輪：只抽「最近一輪為 fixed 或 uncertain」的 key（已 ok 者不再抽）。
  - 配額耗盡或 STOP → 優雅停止，保留已完成結果，重跑時自動斷點續跑。

用法：
  python -X utf8 _src/run_3k_review.py                # 正常執行／斷點接續
  python -X utf8 _src/run_3k_review.py --smoke        # 清空 smoke 輸出並實測 1 檔
  python -X utf8 _src/run_3k_review.py --allow-fail   # 允許略過少數永久失敗檔（如敏感詞）繼續下一輪
環境變數：
  QWEN_MODEL=qwen4-max-preview   # 如要在 2026-11-25 24:00 下線前使用預覽版可覆寫
  QWEN_MAX_TOKENS=262144         # 思考 + 最終回覆總 token 上限
  QWEN_WEB_EXTRACTOR=1           # 1=開啟抓取網頁正文(預設)；0=僅用 web_search 摘要
"""
import argparse
import glob
import io
import json
import os
import random
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
MAX_TOKENS = int(os.environ.get('QWEN_MAX_TOKENS', '262144'))
USE_WEB_EXTRACTOR = os.environ.get('QWEN_WEB_EXTRACTOR', '1') != '0'
WORKERS = 50
ROUNDS = 5

QUOTA = threading.Event()
STOP_REASON = ''
LOG_LOCK = threading.Lock()
RATE_LOCK = threading.Lock()
RATE_UNTIL = 0.0

JSONL_BLK_RE = re.compile(r'<<<JSONL_START>>>\s*(.*?)\s*<<<JSONL_END>>>', re.S)


class QwenStreamError(Exception):
    def __init__(self, code, message):
        super().__init__('%s: %s' % (code, message))
        self.code = str(code or '')
        self.message = str(message or '')


def log(msg):
    line = '[%s] %s' % (time.strftime('%m-%d %H:%M:%S'), msg)
    with LOG_LOCK:
        print(line, flush=True)
        with io.open(os.path.join(ROOT, 'run.log'), 'a', encoding='utf-8') as f:
            f.write(line + '\n')


def stop_flag():
    return os.path.join(ROOT, 'STOP')


def should_stop():
    return QUOTA.is_set() or os.path.exists(stop_flag())


def sleep_interruptible(sec):
    end = time.monotonic() + max(0.0, sec)
    while True:
        if should_stop():
            return False
        rem = end - time.monotonic()
        if rem <= 0:
            return True
        time.sleep(min(1.0, rem))


def bump_cooldown(wait_sec):
    global RATE_UNTIL
    with RATE_LOCK:
        RATE_UNTIL = max(RATE_UNTIL, time.monotonic() + max(1.0, wait_sec))


def wait_cooldown(initial_stagger=False):
    with RATE_LOCK:
        rem = RATE_UNTIL - time.monotonic()
    if rem > 0:
        return sleep_interruptible(rem + random.uniform(1.0, 12.0))
    if initial_stagger:
        return sleep_interruptible(random.uniform(0.0, 4.0))
    return not should_stop()


def load_state():
    p = os.path.join(ROOT, 'state.json')
    if os.path.exists(p):
        with io.open(p, encoding='utf-8-sig') as f:
            return json.load(f)
    return {'rounds_done': [], 'keys': {}}


def save_state(st):
    p = os.path.join(ROOT, 'state.json')
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(st, ensure_ascii=False, indent=1))
    os.replace(tmp, p)


def all_segment_keys():
    """回傳 {key_id: (book_id, rowkey, si, label, seg)}；key_id = book_id|material_key。"""
    out = {}
    for book_id, _, label in M.BOOKS:
        path = os.path.join(B, '定稿', book_id + '.jsonl')
        with io.open(path, encoding='utf-8-sig') as f:
            for ln in f:
                if not ln.strip():
                    continue
                r = json.loads(ln)
                segs = r.get('segments') or []
                for si, s in enumerate(segs, 1):
                    mk = str(r['key']) if len(segs) == 1 else '%s-%d' % (r['key'], si)
                    out['%s|%s' % (book_id, mk)] = (book_id, str(r['key']), si, label, s)
    return out


def format_prompt(book_id):
    """兼容提示詞內含單層 JSON 大括號的寫法，避免 .format() 拋 KeyError。"""
    try:
        return M.PROMPT.format(book_id=book_id)
    except (KeyError, ValueError):
        return M.PROMPT.replace('{book_id}', book_id)


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
            body = format_prompt(book_id) + '\n\n' + '\n'.join(buf)
            with io.open(os.path.join(outdir, name), 'w', encoding='utf-8', newline='\n') as f:
                f.write(body)
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
    with io.open(os.path.join(outdir, '_filekeys.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(filekeys, ensure_ascii=False))
    return idx


def extract_response_text(resp):
    parts = []
    for item in (resp.get('output') or []):
        if item.get('type') != 'message':
            continue
        msg_parts = []
        for c in (item.get('content') or []):
            if c.get('type') == 'output_text' and c.get('text'):
                msg_parts.append(c['text'])
        if msg_parts:
            parts.append(''.join(msg_parts))
    return '\n'.join(parts)


def call_qwen(text, key):
    """以 Token Plan Responses API（串流）呼叫 qwen4-max，確保 completed 且未截斷。"""
    tools = [{'type': 'web_search'}]
    if USE_WEB_EXTRACTOR:
        tools.append({'type': 'web_extractor'})

    payload = {
        'model': MODEL,
        'input': text,
        'reasoning': {'effort': 'xhigh'},
        'tools': tools,
        'max_output_tokens': MAX_TOKENS,
        'store': False,
        'stream': True,
    }
    req = urllib.request.Request(
        BASE + '/responses',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
        },
        method='POST',
    )

    deltas = []
    done_texts = []
    final_resp = None
    terminal_event = None
    stream_err = None

    def handle_sse(ev_name, data_str):
        nonlocal final_resp, terminal_event, stream_err
        if not data_str or data_str == '[DONE]':
            return
        ev = json.loads(data_str)
        t = ev.get('type') or ev_name
        if t == 'response.output_text.delta':
            d = ev.get('delta')
            if d:
                deltas.append(d)
        elif t == 'response.output_text.done':
            txt = ev.get('text')
            if txt is not None:
                done_texts.append(txt)
        elif t in ('response.completed', 'response.incomplete', 'response.failed'):
            terminal_event = t
            final_resp = ev.get('response') or {}
        elif t == 'error':
            stream_err = ev

    with urllib.request.urlopen(req, timeout=1800) as r:
        cur_event = None
        data_buf = []
        for raw in r:
            line = raw.decode('utf-8', errors='replace').rstrip('\r\n')
            if not line:
                if data_buf:
                    handle_sse(cur_event, '\n'.join(data_buf))
                    data_buf = []
                    cur_event = None
                continue
            if line.startswith(':'):
                continue
            if line.startswith('event:'):
                cur_event = line[6:].strip()
            elif line.startswith('data:'):
                data_buf.append(line[5:].lstrip())
        if data_buf:
            handle_sse(cur_event, '\n'.join(data_buf))

    if stream_err is not None:
        err = stream_err.get('error') if isinstance(stream_err.get('error'), dict) else stream_err
        raise QwenStreamError(err.get('code', 'stream_error'), err.get('message', str(stream_err)))

    if terminal_event is None or final_resp is None:
        raise QwenStreamError('stream_truncated', 'stream closed before response.completed')

    status = final_resp.get('status')
    if terminal_event == 'response.failed' or status == 'failed':
        err = final_resp.get('error') or {}
        raise QwenStreamError(err.get('code', 'response_failed'), err.get('message', 'response failed'))

    if terminal_event == 'response.incomplete' or status != 'completed':
        inc = final_resp.get('incomplete_details') or {}
        raise QwenStreamError('incomplete', inc.get('reason') or str(status))

    out_text = extract_response_text(final_resp)
    if out_text:
        return out_text
    if done_texts:
        return ''.join(done_texts)
    return ''.join(deltas)


def strip_fence(s):
    s = s.strip()
    if s.startswith('```'):
        lines = s.splitlines()
        if len(lines) >= 2 and lines[-1].strip() == '```':
            s = '\n'.join(lines[1:-1]).strip()
    return s


def match_key(raw_key, expected_mks=None):
    k = str(raw_key or '').strip()
    if k.startswith('##'):
        k = k[2:].strip()
    if expected_mks:
        exp = set(expected_mks)
        if k in exp:
            return k
        for sep in ('／', '/', '|'):
            if sep in k:
                tail1 = k.split(sep, 1)[1].strip()
                if tail1 in exp:
                    return tail1
                tail2 = k.rsplit(sep, 1)[-1].strip()
                if tail2 in exp:
                    return tail2
    for sep in ('／', '/', '|'):
        if sep in k:
            k = k.rsplit(sep, 1)[-1].strip()
    return k


def extract_jsonl_lines(out):
    matches = JSONL_BLK_RE.findall(out)
    if not matches:
        return None
    blk = strip_fence(matches[-1])
    if not blk:
        return None
    objs = []
    for line in blk.splitlines():
        line = line.strip()
        if not line:
            continue
        o = json.loads(line)
        if not isinstance(o, dict):
            return None
        objs.append(o)
    return objs


def valid(out, expected_mks=None):
    try:
        objs = extract_jsonl_lines(out)
    except Exception:
        return False
    if not objs:
        return False
    got = set()
    for o in objs:
        k = match_key(o.get('key'), expected_mks)
        st = str(o.get('status') or '').strip().lower()
        tr = o.get('translation')
        if not k or st not in ('ok', 'fixed', 'uncertain'):
            return False
        if st == 'fixed' and (not isinstance(tr, str) or not tr.strip()):
            return False
        got.add(k)
    if expected_mks is not None and got != set(expected_mks):
        return False
    return True


def is_fatal_quota_or_auth(code, body_lower):
    if code in (401, 402):
        return True
    if 'datainspection' in body_lower or 'inappropriate' in body_lower or 'content_filter' in body_lower:
        return False
    if code == 403 and any(w in body_lower for w in (
        'unpurchased', 'insufficient_quota', 'subscription', 'arrearage', 'overdue', 'invalidapikey'
    )):
        return True
    if code == 404 and any(w in body_lower for w in ('model_not_found', 'not exist', 'not supported')):
        return True
    if any(w in body_lower for w in (
        'insufficient_quota', 'quota has been exhausted', 'allocationquota'
    )):
        return True
    return False


def run_one(src, outdir, key, expected_mks=None):
    global STOP_REASON
    stem = os.path.basename(src)[:-3]
    dst = os.path.join(outdir, stem + '_回.txt')
    marker = os.path.join(outdir, stem + '.done')
    if os.path.exists(marker) and os.path.exists(dst):
        return 'skip'
    if should_stop():
        return 'stopped'
    with io.open(src, encoding='utf-8-sig') as f:
        text = f.read()

    last = ''
    shape_fails = 0
    for attempt in range(8):
        if not wait_cooldown(initial_stagger=(attempt == 0)):
            return 'stopped'
        try:
            out = call_qwen(text, key).strip()
            if not out:
                last = 'empty'
                shape_fails += 1
                if shape_fails >= 3:
                    break
                sleep_interruptible(5 * shape_fails)
                continue
            if not valid(out, expected_mks):
                last = 'invalid-shape-or-keys'
                shape_fails += 1
                if shape_fails >= 3:
                    break
                sleep_interruptible(5 * shape_fails)
                continue
            with io.open(dst, 'w', encoding='utf-8', newline='\n') as f:
                f.write(out + '\n')
            with io.open(marker, 'w', encoding='utf-8') as f:
                f.write('ok\n')
            return 'ok'
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:400]
            last = 'HTTP%d %s' % (e.code, body[:120])
            low = body.lower()
            if is_fatal_quota_or_auth(e.code, low):
                QUOTA.set()
                STOP_REASON = last
                return 'quota'
            if e.code == 429:
                ra = e.headers.get('Retry-After') if e.headers else None
                try:
                    wait_s = max(60.0, float(ra)) if ra else 60.0
                except ValueError:
                    wait_s = 60.0
                if attempt < 7:
                    bump_cooldown(wait_s)
                    continue
                break
            if e.code in (408, 500, 502, 503, 504) and attempt < 7:
                sleep_interruptible(min(60, 10 * (attempt + 1)) + random.uniform(0.5, 3.0))
                continue
            break
        except QwenStreamError as e:
            last = str(e)[:120]
            low = last.lower()
            if any(w in low for w in ('insufficient_quota', 'quota has been exhausted', 'allocationquota')):
                QUOTA.set()
                STOP_REASON = last
                return 'quota'
            if any(w in low for w in ('rate_limit', 'concurrency', 'too many')):
                if attempt < 7:
                    bump_cooldown(60.0)
                    continue
                break
            if any(w in low for w in ('datainspection', 'inappropriate', 'content_filter')):
                break
            shape_fails += 1
            if shape_fails < 3 and attempt < 7:
                sleep_interruptible(8 * shape_fails)
                continue
            break
        except Exception as e:
            last = type(e).__name__ + ': ' + str(e)[:100]
            if attempt < 7:
                sleep_interruptible(min(45, 8 * (attempt + 1)) + random.uniform(0.5, 2.5))
                continue
            break
    return 'fail ' + last


def run_batch(matdir, outdir, workers, filekeys):
    os.makedirs(outdir, exist_ok=True)
    with io.open(KEY_FILE, encoding='utf-8-sig') as f:
        key = f.read().strip()
    if not key.startswith('sk-sp-'):
        log('警告：Token Plan 應使用 sk-sp- 開頭的專用金鑰（目前前綴=%s）' % key[:6])

    files = sorted(p for p in glob.glob(os.path.join(matdir, '*.md')))
    todo = [
        p for p in files
        if not (
            os.path.exists(os.path.join(outdir, os.path.basename(p)[:-3] + '.done'))
            and os.path.exists(os.path.join(outdir, os.path.basename(p)[:-3] + '_回.txt'))
        )
    ]
    skip = len(files) - len(todo)
    log('batch 待跑 %d／%d workers=%d model=%s web_extractor=%s' % (
        len(todo), len(files), workers, MODEL, USE_WEB_EXTRACTOR))
    if skip:
        log('沿用既有完成 %d 檔' % skip)

    ok = fail = 0
    failed_files = []
    it = iter(todo)
    inflight = {}

    def submit_one(ex, p):
        name = os.path.basename(p)
        mks = [k.split('|', 1)[1] for k in filekeys.get(name, [])]
        return ex.submit(run_one, p, outdir, key, mks if mks else None)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for p in it:
            inflight[submit_one(ex, p)] = p
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
                    failed_files.append({'file': os.path.basename(p), 'reason': st})
                    if st != 'stopped':
                        log('%s %s' % (os.path.basename(p), st))
                if (ok + fail) > 0 and (ok + fail) % 50 == 0:
                    log('ok=%d fail=%d inflight=%d' % (ok, fail, len(inflight)))
            if should_stop():
                continue
            while len(inflight) < workers:
                try:
                    p = next(it)
                except StopIteration:
                    break
                inflight[submit_one(ex, p)] = p

    log('batch 結束 ok=%d fail=%d skip=%d' % (ok, fail, skip))
    return ok, fail, failed_files


def parse_round(outdir, filekeys):
    """回傳 {key_id: (status, translation, note)}；status 為 ok/fixed/uncertain。"""
    res = {}
    for name, kids in filekeys.items():
        expected_mks = [kid.split('|', 1)[1] for kid in kids]
        rp = os.path.join(outdir, name[:-3] + '_回.txt')
        if not os.path.exists(rp):
            for kid in kids:
                res[kid] = ('uncertain', '', '檔案未完成，標記待查')
            continue
        with io.open(rp, encoding='utf-8-sig') as f:
            raw = f.read()
        try:
            objs = extract_jsonl_lines(raw) or []
        except Exception:
            objs = []
        by_mk = {}
        for o in objs:
            mk = match_key(o.get('key'), expected_mks)
            st = str(o.get('status') or '').strip().lower()
            tr = (o.get('translation') or '').strip() if isinstance(o.get('translation'), str) else ''
            note = (o.get('note') or '').strip() if isinstance(o.get('note'), str) else ''
            if mk and st in ('ok', 'fixed', 'uncertain'):
                by_mk[mk] = (st, tr, note)
        for kid in kids:
            _, mk = kid.split('|', 1)
            if mk in by_mk:
                res[kid] = by_mk[mk]
            else:
                res[kid] = ('uncertain', '', '解析缺失，標記待查')
    return res


def apply_fixes(results, keymap, round_no):
    bybook = {}
    for kid, (st, tr, _) in results.items():
        if st != 'fixed' or not tr:
            continue
        bid, rowkey, si, lab, s = keymap[kid]
        bybook.setdefault(bid, []).append((rowkey, si, tr))
    applied = 0
    for bid, fixes in bybook.items():
        path = os.path.join(B, '定稿', bid + '.jsonl')
        bak = os.path.join(B, '定稿', '_舊_%s_before_review_r%d_20261124.jsonl' % (bid, round_no))
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        with io.open(path, encoding='utf-8-sig') as f:
            rows = [json.loads(x) for x in f if x.strip()]
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
        with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    return applied


def latest_fix_keys(st):
    """第 4–5 輪抽最近一輪為 fixed 或 uncertain 的 key 復校。"""
    out = set()
    for kid, hist in st['keys'].items():
        if hist and hist[-1]['status'] in ('fixed', 'uncertain'):
            out.add(kid)
    return out


def do_round(r, st, workers, allow_fail=False):
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

    fk_path = os.path.join(matdir, '_filekeys.json')
    existing_mds = glob.glob(os.path.join(matdir, '*.md')) if os.path.isdir(matdir) else []
    reused = False
    if os.path.exists(fk_path) and existing_mds:
        with io.open(fk_path, encoding='utf-8-sig') as f:
            filekeys = json.load(f)
        if len(existing_mds) == len(filekeys):
            n = len(filekeys)
            reused = True
            log('round%d 沿用既有材料 %d 檔（斷點續跑）' % (r, n))
    if not reused:
        n = gen_materials(matdir, keymap, target)
        with io.open(fk_path, encoding='utf-8-sig') as f:
            filekeys = json.load(f)
        log('round%d 材料 %d 檔（target=%s）' % (r, n, '全量' if target is None else len(target)))

    _, fail, failed_files = run_batch(matdir, outdir, workers, filekeys)
    failed_path = os.path.join(rdir, 'failed.json')
    if failed_files:
        with io.open(failed_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(failed_files, ensure_ascii=False, indent=1))
    elif os.path.exists(failed_path):
        os.remove(failed_path)

    if should_stop() or (fail > 0 and not allow_fail):
        log('round%d 未全部完成（fail=%d stopped=%s），保留已完成輸出；不套用修正、不標記 rounds_done，修復後重跑即可接續' % (
            r, fail, should_stop()))
        return False

    results = parse_round(outdir, filekeys)
    applied = apply_fixes(results, keymap, r)
    counts = {'ok': 0, 'fixed': 0, 'uncertain': 0}
    for kid, (stt, tr, note) in results.items():
        counts[stt] = counts.get(stt, 0) + 1
        st['keys'].setdefault(kid, []).append({'round': r, 'status': stt})
    st['rounds_done'].append(r)
    save_state(st)
    log('round%d 完成：ok=%d fixed=%d uncertain=%d、套用 %d、累計 key %d' % (
        r, counts['ok'], counts['fixed'], counts['uncertain'], applied, len(st['keys'])))
    with io.open(os.path.join(rdir, 'summary.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({
            'round': r,
            'files': n,
            'counts': counts,
            'applied': applied,
            'failed_files': failed_files,
            'results': {
                k: ({'status': v[0], 'note': v[2]} if v[2] else {'status': v[0]})
                for k, v in results.items()
            },
        }, ensure_ascii=False, indent=1))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--workers', type=int, default=WORKERS)
    ap.add_argument('--rounds', type=int, default=ROUNDS,
                    help='跑到第幾輪為止（預設 %d；今晚只跑一輪可用 1）' % ROUNDS)
    ap.add_argument('--allow-fail', action='store_true',
                    help='非 stop/配額中斷時，允許略過 failed.json 檔案繼續套用與下一輪')
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    if a.smoke:
        keymap = all_segment_keys()
        matdir = os.path.join(ROOT, 'smoke', '材料')
        outdir = os.path.join(ROOT, 'smoke', '輸出')
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)
        first = next(iter(keymap))
        gen_materials(matdir, keymap, {first})
        with io.open(os.path.join(matdir, '_filekeys.json'), encoding='utf-8-sig') as f:
            filekeys = json.load(f)
        run_batch(matdir, outdir, 1, filekeys)
        parsed = parse_round(outdir, filekeys)
        for p in glob.glob(os.path.join(outdir, '*_回.txt')):
            with io.open(p, encoding='utf-8-sig') as f:
                log('SMOKE %s -> %s' % (os.path.basename(p), f.read()[:160]))
        log('SMOKE parsed -> %s' % json.dumps(parsed, ensure_ascii=False))
        return

    st = load_state()
    for r in range(1, max(1, a.rounds) + 1):
        if r in st['rounds_done']:
            log('round%d 已完成，跳過' % r)
            continue
        if os.path.exists(stop_flag()):
            log('STOP 存在，停止')
            break
        cont = do_round(r, st, a.workers, allow_fail=a.allow_fail)
        if not cont:
            log('配額耗盡／停止／有失敗檔，保留結果，退出。reason=%s' % STOP_REASON)
            break
    log('orchestrator 結束 rounds_done=%s' % st['rounds_done'])


if __name__ == '__main__':
    main()