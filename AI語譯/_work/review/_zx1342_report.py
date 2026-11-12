# -*- coding: utf-8 -*-
"""從 _zx1342_log 產生逐檔統計表（給說明用）。"""
import os, sys, json, glob, re
sys.path.insert(0, os.path.dirname(__file__))
import _zx1342_lib as L

LOGD = os.path.join(os.path.dirname(__file__), '_zx1342_log')
rows = []
for p in sorted(glob.glob(os.path.join(LOGD, 'log_*.json'))):
    n = int(re.search(r'log_(\d+)', p).group(1))
    d = json.load(open(p, encoding='utf-8'))
    ne = 0
    segs = 0
    chunks = []
    for c in d['chunks']:
        ne += len(c['edits'])
        segs += len(c['changed'])
        chunks.append('%s#%s' % (c['chunk'], ','.join(str(x) for x in c['changed'])))
    recs = L.parse_review(n)
    rows.append((n, len(recs), ne, segs, '；'.join(chunks)))

out = ['| 檔 | 材料段數 | 改處 | 改段 | 改動段號 |', '|---|---|---|---|---|']
te = ts = tn = 0
for n, ns, ne, segs, ch in rows:
    out.append('| %d | %d | %d | %d | %s |' % (n, ns, ne, segs, ch))
    tn += ns; te += ne; ts += segs
out.append('| 合計 | %d | %d | %d | — |' % (tn, te, ts))
p = os.path.join(os.path.dirname(__file__), '_zx1342_report.md')
open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('files=%d segs=%d edits=%d changedsegs=%d' % (len(rows), tn, te, ts))
