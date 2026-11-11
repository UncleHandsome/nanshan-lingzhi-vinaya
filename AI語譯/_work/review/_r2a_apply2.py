# -*- coding: utf-8 -*-
"""套用某檔的 edits json（容忍模式）。
用法: python _r2a_apply1.py edits.json [--dry] [--tolerant]
tolerant: 逐條檢查，失敗者列出並跳過，只套用成功者。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

path = sys.argv[1]
dry = '--dry' in sys.argv
tol = '--tolerant' in sys.argv
d = json.load(open(path, encoding='utf-8-sig'))
n = d['n']
edits = d.get('edits', [])

if not tol:
    by = {}
    for e in edits:
        by.setdefault((e['book'], e['chunk']), []).append(e)
    logs = []
    for (book, chunk), es in by.items():
        lg = L.apply_edits(book, chunk, es, dry=dry)
        logs += lg
        print('OK %s/%s: %d edits' % (book, chunk, len(es)))
    if not dry:
        L.append_done(n)
        logdir = os.path.join(os.path.dirname(__file__), '_r2a_log')
        os.makedirs(logdir, exist_ok=True)
        with open(os.path.join(logdir, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
            json.dump(dict(n=n, edits=logs, verdicts=d.get('verdicts', [])), f, ensure_ascii=False, indent=1)
    print('applied %d edits for %d' % (len(logs), n))
    sys.exit(0)

# tolerant: 先按 chunk/seg 檢查
cache = {}
ok, bad = [], []
for e in edits:
    key = (e['book'], e['chunk'])
    if key not in cache:
        cache[key] = L.Out(*key)
    o = cache[key]
    if not (0 <= e['seg'] - 1 < len(o.segs)):
        bad.append((e, 'RANGE'))
        continue
    c = o.segs[e['seg'] - 1].count(e['old'])
    if c != 1:
        bad.append((e, 'COUNT=%d' % c))
    else:
        ok.append(e)
print('MATCH %d / BAD %d' % (len(ok), len(bad)))
for e, why in bad[:40]:
    print('BAD %s#%d %s | %s' % (e['chunk'], e['seg'], why, e['old'][:50]))
if ok and not dry:
    by = {}
    for e in ok:
        by.setdefault((e['book'], e['chunk']), []).append(e)
    logs = []
    for (book, chunk), es in by.items():
        logs += L.apply_edits(book, chunk, es)
        print('OK %s/%s: %d edits' % (book, chunk, len(es)))
    L.append_done(n)
    logdir = os.path.join(os.path.dirname(__file__), '_r2a_log')
    os.makedirs(logdir, exist_ok=True)
    with open(os.path.join(logdir, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
        json.dump(dict(n=n, edits=logs, bad=[dict(chunk=e['chunk'], seg=e['seg'], old=e['old'], why=w) for e, w in bad]), f, ensure_ascii=False, indent=1)
