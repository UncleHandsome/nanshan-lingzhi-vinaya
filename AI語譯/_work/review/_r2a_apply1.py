# -*- coding: utf-8 -*-
"""套用某檔的 edits json。
json 格式: {"n":1000, "edits":[{"book":..,"chunk":..,"seg":9,"old":..,"new":..,"why":..}],
            "verdicts":[{"seq":1,"kind":"誤報","reason":..}, ...]}
用法: python _r2a_apply1.py edits_1000.json [--dry]
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

path = sys.argv[1]
dry = '--dry' in sys.argv
d = json.load(open(path, encoding='utf-8-sig'))
n = d['n']
edits = d.get('edits', [])
by = {}
for e in edits:
    by.setdefault((e['book'], e['chunk']), []).append(e)
logs = []
for (book, chunk), es in by.items():
    try:
        lg = L.apply_edits(book, chunk, es, dry=dry)
        logs += lg
        print('OK %s/%s: %d edits' % (book, chunk, len(es)))
    except SystemExit as ex:
        print('FAIL %s/%s: %s' % (book, chunk, ex))
        raise
if not dry:
    L.append_done(n)
    logdir = os.path.join(os.path.dirname(__file__), '_r2a_log')
    os.makedirs(logdir, exist_ok=True)
    with open(os.path.join(logdir, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
        json.dump(dict(n=n, edits=logs, verdicts=d.get('verdicts', [])), f, ensure_ascii=False, indent=1)
print('applied %d edits for %d' % (len(logs), n))
