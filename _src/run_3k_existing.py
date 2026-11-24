# -*- coding: utf-8 -*-
"""跑 3K 審閱材料（既有材料，不重產）：由小到大、不重試、逐檔記時間。

每檔落盤：
  六書_3K_跑_20261124/輸出/<stem>_回.txt   原始回覆（非空才算完成，續跑跳過）
  六書_3K_跑_20261124/progress.jsonl       逐檔 t_start／t_end／dur_s／token
  六書_3K_跑_20261124/usage.json           累計 token 與狀態數
  六書_3K_跑_20261124/run.log              心跳（每 60 秒）
  六書_3K_跑_20261124/fixes.jsonl          可套用修正（不自動套用）
跑完另出 summary.json、時間表.csv。
STOP 檔 → 停送新檔；全域 90 分鐘零完成 → 視為卡死停送。
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
import book_prompt

B = R.B
MAT = os.path.join(B, '六書_3K_20261124')
OUT = os.path.join(B, '六書_3K_跑_20261124')
RAW = os.path.join(OUT, '輸出')
PROG = os.path.join(OUT, 'progress.jsonl')
USAGE_F = os.path.join(OUT, 'usage.json')
FIXES = os.path.join(OUT, 'fixes.jsonl')
STOP = os.path.join(OUT, 'STOP')
WORKERS = int(os.environ.get('RUN_WORKERS', '80'))
STALL_SEC = int(os.environ.get('RUN_STALL_SEC', '5400'))
LOCK = threading.Lock()
HALT = threading.Event()
USAGE = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
STAT = {'ok': 0, 'skip': 0, 'fail': 0, 'done': 0, 'total': 0,
        'fixed': 0, 'uncertain': 0, 'ok_seg': 0}
LAST_DONE = [time.time()]
T0 = time.time()
NAME2ID = {v['name']: k for k, v in book_prompt.PROFILES.items()}


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
        atomic_write(USAGE_F, json.dumps(
            {'usage': USAGE, 'stat': STAT, 'elapsed_s': int(time.time() - T0)},
            ensure_ascii=False, indent=1))


def heartbeat():
    while not HALT.wait(60):
        idle = int(time.time() - LAST_DONE[0])
        log('heartbeat done=%d/%d ok=%d fail=%d skip=%d in_flight=%d idle_s=%d elapsed=%ds usage=%s' % (
            STAT['done'], STAT['total'], STAT['ok'], STAT['fail'], STAT['skip'],
            max(0, STAT['total'] - STAT['done']), idle, int(time.time() - T0), USAGE))
        if idle > STALL_SEC and STAT['done'] > 0:
            log('全域 %d 秒零完成 → 視為卡死，停止送新檔' % idle)
            HALT.set()


def parse_reply(stem, text):
    book = stem.rsplit('_', 1)[-1]
    exp = [(NAME2ID.get(m.group(1)) or m.group(1), m.group(2).strip())
           for m in re.finditer(r'^##\s+([^／\n]+)／(.+?)\s*$', text, re.M)]
    exp = [(b, k) for b, k in exp if b]
    if not exp:
        return
    rp = os.path.join(RAW, stem + '_回.txt')
    if not os.path.exists(rp):
        return
    raw = io.open(rp, encoding='utf-8').read()
    try:
        objs = R.extract_jsonl_lines(raw) or []
    except Exception:
        objs = []
    exp_mks = [k for _, k in exp]
    book0 = exp[0][0]
    for o in objs:
        mk = R.match_key(o.get('key'), exp_mks)
        st = str(o.get('status') or '').strip().lower()
        tr = (o.get('translation') or '').strip() if isinstance(o.get('translation'), str) else ''
        if st == 'fixed' and tr:
            append_jsonl(FIXES, {'book': book0, 'mk': mk, 'translation': tr})
            STAT['fixed'] += 1
        elif st == 'uncertain':
            STAT['uncertain'] += 1
        elif st == 'ok':
            STAT['ok_seg'] += 1


def one(path, key):
    stem = os.path.basename(path)[:-3]
    dst = os.path.join(RAW, stem + '_回.txt')
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return stem, 'skip', {}, 0.0, 0.0, 0.0
    if HALT.is_set() or os.path.exists(STOP):
        return stem, 'halt', {}, 0.0, 0.0, 0.0
    text = io.open(path, encoding='utf-8').read()
    ts = time.time()
    t_start = time.strftime('%H:%M:%S', time.localtime(ts))
    usage = {}
    try:
        out = R.call_qwen(text, key, usage)
    except R.QwenStreamError as e:
        te = time.time()
        return stem, 'fail %s: %s' % (e.code, (e.message or '')[:90]), {}, t_start, \
            time.strftime('%H:%M:%S', time.localtime(te)), round(te - ts, 1)
    except Exception as e:
        te = time.time()
        return stem, 'fail %s: %s' % (type(e).__name__, str(e)[:80]), {}, t_start, \
            time.strftime('%H:%M:%S', time.localtime(te)), round(te - ts, 1)
    te = time.time()
    t_end = time.strftime('%H:%M:%S', time.localtime(te))
    io.open(dst, 'w', encoding='utf-8', newline='\n').write(out)
    return stem, 'ok', usage, t_start, t_end, round(te - ts, 1)


def main():
    if '--apply' in sys.argv:
        apply_fixes()
        return
    os.makedirs(RAW, exist_ok=True)
    key = io.open(R.KEY_FILE, encoding='utf-8-sig').read().strip()
    files = [p for p in glob.glob(os.path.join(MAT, '*.md'))
             if os.path.basename(p) != 'README.md']
    done_set = set(os.path.basename(f)[:-6] for f in glob.glob(os.path.join(RAW, '*_回.txt'))
                   if os.path.getsize(f) > 0)
    files = [p for p in files if os.path.basename(p)[:-3] not in done_set]
    files.sort(key=lambda p: os.path.getsize(p))
    limit = int(os.environ.get('RUN_LIMIT', '0'))
    if limit:
        files = files[:limit]
    STAT['total'] = len(files)
    log('start: todo=%d (existing replies skipped %d) workers=%d timeout=%ss deadline=%ss idle=%ss'
        % (len(files), len(done_set), WORKERS, R.CALL_TIMEOUT, R.CALL_DEADLINE, R.CALL_IDLE))
    if not files:
        log('nothing to do')
        return
    threading.Thread(target=heartbeat, daemon=True).start()
    times = []
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(one, p, key): p for p in files}
            for f in as_completed(futs):
                stem, st, usage, ts, te, dur = f.result()
                STAT['done'] += 1
                LAST_DONE[0] = time.time()
                if st == 'ok':
                    STAT['ok'] += 1
                    USAGE['calls'] += 1
                    for k in ('input_tokens', 'output_tokens', 'total_tokens'):
                        if isinstance(usage.get(k), int):
                            USAGE[k] += usage[k]
                    parse_reply(stem, io.open(futs[f], encoding='utf-8').read())
                    times.append((stem, dur, 'ok'))
                elif st == 'skip':
                    STAT['skip'] += 1
                elif st == 'halt':
                    STAT['skip'] += 1
                else:
                    STAT['fail'] += 1
                    times.append((stem, dur, st[:60]))
                append_jsonl(PROG, {'t': time.strftime('%H:%M:%S'), 'file': stem, 'status': st[:90],
                                    't_start': ts, 't_end': te, 'dur_s': dur,
                                    'usage': usage, 'done': STAT['done'], 'total': STAT['total']})
                flush_usage()
                if STAT['done'] % 25 == 0 or st.startswith('fail'):
                    log('progress %d/%d %s %s dur=%ss usage=%s' % (
                        STAT['done'], STAT['total'], stem, st[:40], dur, USAGE))
    except KeyboardInterrupt:
        log('KeyboardInterrupt：停止送新檔')
    finally:
        HALT.set()
        flush_usage()
        write_summary(times)
        log('DONE done=%d/%d elapsed=%ds usage=%s stat=%s' % (
            STAT['done'], STAT['total'], int(time.time() - T0), USAGE, STAT))


def write_summary(times):
    ok = [t for t in times if t[2] == 'ok']
    slow = sorted(ok, key=lambda x: -x[1])[:20]
    summary = {
        'elapsed_s': int(time.time() - T0),
        'elapsed_h': round((time.time() - T0) / 3600, 2),
        'todo': STAT['total'], 'done': STAT['done'], 'ok': STAT['ok'],
        'fail': STAT['fail'], 'skip': STAT['skip'],
        'usage': USAGE,
        'avg_ok_s': round(sum(t[1] for t in ok) / len(ok), 1) if ok else None,
        'slowest20': [{'file': f, 'dur_s': d} for f, d, _ in slow],
    }
    atomic_write(os.path.join(OUT, 'summary.json'),
                 json.dumps(summary, ensure_ascii=False, indent=1))
    rows = ['file,dur_s,status'] + ['%s,%s,%s' % (f, d, s) for f, d, s in sorted(times, key=lambda x: -x[1])]
    io.open(os.path.join(OUT, '時間表.csv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    log('summary: avg_ok_s=%s slowest=%s' % (
        summary['avg_ok_s'], summary['slowest20'][:3]))


def apply_fixes():
    keymap = R.all_segment_keys()
    latest = {}
    if os.path.exists(FIXES):
        for ln in io.open(FIXES, encoding='utf-8'):
            if not ln.strip():
                continue
            o = json.loads(ln)
            latest[(o['book'], o['mk'])] = o['translation']
    if not latest:
        log('no fixes to apply')
        return
    bybook = {}
    for (book, mk), tr in latest.items():
        kid = '%s|%s' % (book, mk)
        if kid not in keymap:
            continue
        _, rowkey, si, lab, seg = keymap[kid]
        bybook.setdefault(book, []).append((rowkey, si, tr))
    total = 0
    for book, fixes in bybook.items():
        path = os.path.join(B, '定稿', book + '.jsonl')
        bak = path + '.bak_run3k_%s.jsonl' % time.strftime('%Y%m%d_%H%M%S')
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        bykey = {str(r['key']): r for r in rows}
        n = 0
        for rowkey, si, tr in fixes:
            r = bykey.get(rowkey)
            if not r:
                continue
            segs = r.get('segments') or []
            if 1 <= si <= len(segs):
                segs[si - 1]['translation'] = tr
                r['translation'] = '\n\n'.join((s.get('translation') or '') for s in segs)
                n += 1
        if n:
            if not os.path.exists(bak):
                import shutil
                shutil.copy2(path, bak)
            io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
        total += n
        log('applied %s %d' % (book, n))
    log('apply total %d' % total)


if __name__ == '__main__':
    main()
