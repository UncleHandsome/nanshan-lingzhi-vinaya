# -*- coding: utf-8 -*-
"""統計 _r2c_log/log_N.json（1533 起）。用法: python _r2d_stat.py [起] [迄]"""
import os, sys, json, io, collections
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log')
a = int(sys.argv[1]) if len(sys.argv) > 1 else 1533
b = int(sys.argv[2]) if len(sys.argv) > 2 else 1648
tot = collections.Counter()
files = 0
print('| 檔 | 改段 | 改處 | 真錯 | 誤報 | 存疑 | 其他 |')
print('|---|---|---|---|---|---|---|')
for n in range(a, b + 1):
    p = os.path.join(D, 'log_%d.json' % n)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    edits = d.get('edits', [])
    segs = len(set((e['chunk'], e['seg']) for e in edits))
    c = collections.Counter(v.get('kind', '?') for v in d.get('verdicts', []))
    other = sum(v for k, v in c.items() if k not in ('真錯', '誤報', '存疑'))
    print('| %d | %d | %d | %d | %d | %d | %d |' % (
        n, segs, len(edits), c.get('真錯', 0), c.get('誤報', 0), c.get('存疑', 0), other))
    files += 1
    tot.update(c)
    tot['改段'] += segs
    tot['改處'] += len(edits)
print('| 合計 | %d | %d | %d | %d | %d | %d |' % (
    tot['改段'], tot['改處'], tot.get('真錯', 0), tot.get('誤報', 0), tot.get('存疑', 0),
    sum(v for k, v in tot.items() if k not in ('真錯', '誤報', '存疑', '改段', '改處'))))
print('FILES=%d' % files)
