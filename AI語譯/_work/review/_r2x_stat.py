# -*- coding: utf-8 -*-
"""統計 log_<n>.json：改段、改處、真錯、否決、存疑。用法: python _r2x_stat.py 1775 1790"""
import json, io, sys, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log')
a, b = int(sys.argv[1]), int(sys.argv[2])
tot = collections.Counter()
print('| 檔 | 改段 | 改處 | 真錯 | 否決 | 存疑 |')
print('|---|---|---|---|---|---|')
for n in range(a, b + 1):
    p = os.path.join(D, 'log_%d.json' % n)
    if not os.path.exists(p):
        print('| %d | — | — | — | — | — |' % n)
        continue
    d = json.load(open(p, encoding='utf-8'))
    segs = len(set(e['seg'] for e in d['edits']))
    v = collections.Counter(x['kind'] for x in d.get('verdicts', []))
    print('| %d | %d | %d | %d | %d | %d |' % (n, segs, len(d['edits']),
          v['真錯'], v['誤報'], v['存疑']))
    tot['segs'] += segs
    tot['edits'] += len(d['edits'])
    tot['z'] += v['真錯']
    tot['f'] += v['誤報']
    tot['c'] += v['存疑']
    tot['files'] += 1
print('TOTAL files=%d segs=%d edits=%d 真錯=%d 否決=%d 存疑=%d' % (
    tot['files'], tot['segs'], tot['edits'], tot['z'], tot['f'], tot['c']))
