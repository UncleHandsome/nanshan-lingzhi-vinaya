# -*- coding: utf-8 -*-
"""由 log 抽出存疑，append 到 存疑材料/r2_存疑/資持記.md"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_zx1031_log')
rows = []
for fn in sorted(os.listdir(LOG)):
    if not fn.startswith('log_'): continue
    n = int(fn[4:-5])
    if not (1031 <= n <= 1180): continue
    d = json.load(open(os.path.join(LOG, fn), encoding='utf-8'))
    for v in d.get('verdicts', []):
        if v['kind'] == '存疑':
            rows.append((n, v['seq'], v['reason']))
# 取 chunk/seg 對照
import _r2a_lib
mp = {}
for n, seq, reason in rows:
    if n not in mp:
        mp[n] = {r['seq']: (r['book'], r['chunk'], r['seg']) for r in L.parse_review(n)}
    b, c, s = mp[n][seq]
    print('%d-000%d %s/%s#%d %s' % (n, seq, b, c, s, reason))
