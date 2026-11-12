# -*- coding: utf-8 -*-
import json, os
D = '_r2c_log'
segs = edits = z = f = c = files = 0
for n in range(1811, 1832):
    p = os.path.join(D, 'log_%d.json' % n)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    files += 1
    segs += len(set(e['seg'] for e in d['edits']))
    edits += len(d['edits'])
    for v in d.get('verdicts', []):
        k = v['kind']
        if k == '真錯': z += 1
        elif k == '誤報': f += 1
        elif k == '存疑': c += 1
print(files, segs, edits, z, f, c)
