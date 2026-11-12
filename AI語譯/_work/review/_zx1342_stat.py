# -*- coding: utf-8 -*-
"""統計每檔 resp 的「可動條目」數量與密度，用於排批次。
輸出 _zx1342_stat.txt
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _zx1342_lib as L

ACT = re.compile(r'必改|重大|建議|宜作|宜改|宜譯|應改|應作|改為|改作|修正|錯誤|誤解|誤譯|譯錯|漏譯|增譯|不符|相反|顛倒|❌|★|不通|矛盾|失當|錯')
NEG = re.compile(r'無誤|沒有問題|無須修改|不必修改|無意見|全檔無|未發現|均可|可從|無錯')
rows = []
for n in range(1342, 1491):
    p = os.path.join(L.RESP, 'resp_%04d.txt' % n)
    if not os.path.exists(p):
        rows.append((n, -1, 0, 0, 'MISSING'))
        continue
    t = open(p, encoding='utf-8-sig').read().replace('\r\n', '\n')
    lines = [x.strip() for x in t.split('\n') if x.strip()]
    hits = [x for x in lines if ACT.search(x)]
    negs = [x for x in lines if NEG.search(x)]
    rows.append((n, len(hits), len(lines), len(t), ''))
out = []
for n, h, ln, sz, tag in rows:
    out.append('%d\thits=%d\tlines=%d\tchars=%d\t%s' % (n, h, ln, sz, tag))
dst = os.path.join(os.path.dirname(__file__), '_zx1342_stat.txt')
open(dst, 'w', encoding='utf-8').write('\n'.join(out))
tot = [r for r in rows if r[1] >= 0]
print('files', len(rows), 'missing', sum(1 for r in rows if r[1] < 0))
buckets = {}
for n, h, ln, sz, tag in rows:
    b = 0 if h <= 1 else 1 if h <= 3 else 2 if h <= 6 else 3
    buckets[b] = buckets.get(b, 0) + 1
print('hits<=1:%d 2-3:%d 4-6:%d >6:%d' % (buckets.get(0, 0), buckets.get(1, 0),
                                           buckets.get(2, 0), buckets.get(3, 0)))
print('total hits', sum(r[1] for r in tot if r[1] > 0))
