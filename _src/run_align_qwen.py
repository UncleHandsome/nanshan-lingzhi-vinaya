# -*- coding: utf-8 -*-
"""文意對位：用千問 API 跑既有材料（對位材料_20261125），WORKER 可調。

每檔逐檔落盤：
  對位結果_20261125/回/<stem>_回.txt   原始回覆（resume 用）
  對位結果_20261125/<stem>.jsonl      解析後的對位
  progress.jsonl / usage.json          每檔更新
  STOP                                停止送新檔
跑完可續跑（已有 .jsonl 者跳過）。
"""
import glob
import io
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
import run_3k_review as R

B = R.B
MAT = os.path.join(B, '對位材料_20261125')
OUT = os.path.join(B, '對位結果_20261125')
RAW = os.path.join(OUT, '回')
PROG = os.path.join(OUT, 'progress.jsonl')
USAGE_F = os.path.join(OUT, 'usage.json')
STOP = os.path.join(OUT, 'STOP')
WORKERS = int(os.environ.get('ALIGN_WORKERS', '40'))
LOCK = threading.Lock()
QUOTA = threading.Event()
USAGE = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
STAT = {'ok': 0, 'skip': 0, 'fail': 0, 'fixed': 0, 'orphan': 0, 'missing': 0, 'done': 0, 'total': 0}
HB_STOP = threading.Event()


def heartbeat():
    t0 = time.time()
    while not HB_STOP.wait(60):
        log('heartbeat done=%d/%d calls=%d in_flight=%d elapsed=%ds usage=%s' % (
            STAT['done'], STAT['total'], USAGE['calls'],
            max(0, STAT['total'] - STAT['done']), int(time.time() - t0), USAGE))


def log(msg):
    line = '[%s] %s' % (time.strftime('%m-%d %H:%M:%S'), msg)
    print(line, flush=True)
    try:
        io.open(os.path.join(OUT, 'run.log'), 'a', encoding='utf-8').write(line + '\n')
    except Exception:
        pass


def atomic_write(path, text):
    tmp = path + '.tmp'
    io.open(tmp, 'w', encoding='utf-8', newline='\n').write(text)
    os.replace(tmp, path)


def append_jsonl(path, obj):
    with LOCK:
        with io.open(path, 'a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def flush_usage():
    with LOCK:
        atomic_write(USAGE_F, json.dumps({'usage': USAGE, 'stat': STAT}, ensure_ascii=False, indent=1))


def load_windows():
    w = json.load(io.open(os.path.join(MAT, '_windows.json'), encoding='utf-8'))
    bypian = {}
    for x in w:
        bypian.setdefault(x['pian'], set()).update(x['chao_keys'])
    for x in w:
        x['pian_chao'] = bypian[x['pian']]
    return {x['file'][:-3]: x for x in w}


def norm_key(x):
    s = str(x or '').strip()
    for pre in ('記', '鈔', '记', '钞', '記段', '鈔段'):
        if s.startswith(pre):
            s = s[len(pre):].strip()
            break
    return s.strip().strip('[]「」')


def parse_objs(raw):
    """從回覆抓 JSON 物件（每行一個，容忍 ```json fence）。"""
    objs = []
    for ln in (raw or '').split('\n'):
        s = ln.strip()
        if s.startswith('```'):
            continue
        if not s.startswith('{'):
            continue
        try:
            o = json.loads(s)
        except Exception:
            continue
        if isinstance(o, dict) and 'B' in o:
            objs.append(o)
    return objs


def one(path, key, win):
    stem = os.path.basename(path)[:-3]
    dst = os.path.join(OUT, stem + '.jsonl')
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        n = sum(1 for _ in io.open(dst, encoding='utf-8'))
        return stem, 'skip', {}, n
    if QUOTA.is_set() or os.path.exists(STOP):
        return stem, 'quota', {}, 0
    rawpath = os.path.join(RAW, stem + '_回.txt')
    text = io.open(path, encoding='utf-8').read()
    usage = {}
    last = ''
    out = ''
    for attempt in range(3):
        try:
            out = R.call_qwen(text, key, usage)
            break
        except R.QwenStreamError as e:
            last = '%s: %s' % (e.code, e.message[:120])
            if R.is_fatal_quota_or_auth(str(e.code), (e.message or '').lower()):
                QUOTA.set()
                return stem, 'quota', {}, 0
            time.sleep(8 * (attempt + 1))
        except Exception as e:
            last = type(e).__name__ + ': ' + str(e)[:120]
            time.sleep(8 * (attempt + 1))
    if not out:
        return stem, 'fail ' + last, {}, 0
    io.open(rawpath, 'w', encoding='utf-8', newline='\n').write(out)
    objs = parse_objs(out)
    if not objs:
        return stem, 'fail no-jsonl', {}, 0
    ji = set(win['ji_keys'])
    chao = win.get('pian_chao') or set(win['chao_keys'])
    lines = []
    seen = set()
    orph = 0
    for o in objs:
        b = norm_key(o.get('B'))
        if b not in ji or b in seen:
            continue
        seen.add(b)
        a = [norm_key(x) for x in (o.get('A') or [])]
        a = [x for x in a if x in chao]
        typ = str(o.get('type') or '').strip() or ('orphan' if not a else ('1:1' if len(a) == 1 else '1:n'))
        if not a:
            typ = 'orphan'; orph += 1
        lines.append(json.dumps({'B': b, 'A': a, 'type': typ,
                                 'why': str(o.get('why') or '')[:200]}, ensure_ascii=False))
    missing = len(ji - seen)
    io.open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + ('\n' if lines else ''))
    with LOCK:
        STAT['fixed'] += len(lines); STAT['orphan'] += orph; STAT['missing'] += missing
    return stem, 'ok', usage, len(lines), missing, orph


def main():
    os.makedirs(RAW, exist_ok=True)
    key = io.open(R.KEY_FILE, encoding='utf-8-sig').read().strip()
    wins = load_windows()
    files = [p for p in glob.glob(os.path.join(MAT, '*.md'))
             if os.path.basename(p) != 'README.md' and os.path.basename(p)[:-3] in wins]
    files.sort(key=lambda p: -os.path.getsize(p))
    if os.environ.get('ALIGN_SMALL', '0') == '1':
        files.sort(key=lambda p: os.path.getsize(p))
    limit = int(os.environ.get('ALIGN_LIMIT', '0'))
    if limit:
        files = files[:limit]
    log('start align: files=%d workers=%d socket=%ss deadline=%ss idle=%ss' % (
        len(files), WORKERS, R.CALL_TIMEOUT, R.CALL_DEADLINE, R.CALL_IDLE))
    STAT['total'] = len(files)
    HB_STOP.clear()
    threading.Thread(target=heartbeat, daemon=True).start()
    done = 0
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(one, p, key, wins[os.path.basename(p)[:-3]]): p for p in files}
            for f in as_completed(futs):
                res = f.result()
                stem, st, usage = res[0], res[1], res[2]
                done += 1
                STAT['done'] = done
                if st == 'ok':
                    USAGE['calls'] += 1
                    for k in ('input_tokens', 'output_tokens', 'total_tokens'):
                        if isinstance(usage.get(k), int):
                            USAGE[k] += usage[k]
                    STAT['ok'] += 1
                elif st == 'skip':
                    STAT['skip'] += 1
                elif st == 'quota':
                    STAT['skip'] += 1
                else:
                    STAT['fail'] += 1
                append_jsonl(PROG, {'t': time.strftime('%H:%M:%S'), 'file': stem, 'status': st[:90],
                                    'usage': usage, 'done': done, 'total': len(files),
                                    'lines': res[3] if len(res) > 3 else 0})
                flush_usage()
                if done % 10 == 0 or st.startswith('fail'):
                    log('progress %d/%d %s %s usage=%s stat=%s' % (
                        done, len(files), stem, st[:40], USAGE, STAT))
    except KeyboardInterrupt:
        log('KeyboardInterrupt：停止送新檔')
    finally:
        flush_usage()
        log('DONE done=%d/%d usage=%s stat=%s' % (done, len(files), USAGE, STAT))


if __name__ == '__main__':
    main()
