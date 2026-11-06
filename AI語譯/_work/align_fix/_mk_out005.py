# -*- coding: utf-8 -*-
"""Build out_005.json for align_fix batch 005.

Batch 005 = 篇13 篇聚名報.
items  z0..z11 = 資持記 paragraphs 0..11 of the 篇 (釋篇題 + 釋「敘意」初科/次科/三明損/四立篇).
cand   c0..c25 = 行事鈔 paragraphs of 篇13 (c0 = 序「出俗五眾…」; c1 = 「初中，所以犯戒果報…」;
                 c2 = 「二者列名釋位…」 …).

Every one of the 12 記 paragraphs 牒解 the 鈔 序 (c0): the 篇題釋 (篇聚者，攝犯之大科…),
「敘意」初科 (出俗五眾…實由戒體故也), 次科 (今若氷潔其心… / 不然縱拒，自貽伊戚…),
二八之獄 (《智論》十六獄), 「故五篇明犯…」, 「而新學之徒…」, 「故《毘尼母論》云…」,
「然則，業隨心結…」(四立篇).  The 記 for 鈔 c1 begins only at 記 paragraph 15
(「開章中。科云先明戒護者…」), which is not in this batch.
"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
d = json.load(io.open(os.path.join(AD, '005.json'), encoding='utf-8'))
items = d['items']
cset = [c['c'] for c in d['cand']]

res = [{'z': it['z'], 'c': 0} for it in items]

assert len(res) == len(items)
assert all(r['c'] in cset for r in res)
assert all(res[i]['c'] <= res[i + 1]['c'] for i in range(len(res) - 1))
io.open(os.path.join(AD, 'out_005.json'), 'w', encoding='utf-8').write(
    json.dumps({'map': res}, ensure_ascii=False, separators=(',', ':')))
print('written', len(res))
