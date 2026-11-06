#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '024.json'), encoding='utf-8'))
hb = json.load(open(os.path.join(HERE, '_a024_hb.json'), encoding='utf-8'))
J = [t for k, t in hb if k == 'J']
C = [t for k, t in hb if k == 'C']
items = d['items']
cand = d['cand']
out = []
out.append(f"items={len(items)} cand={len(cand)} J={len(J)} C={len(C)}")
# check item text vs hebian J (strip 【記】)
ok = 0
mism = []
for i, it in enumerate(items):
    jt = J[i].replace('【記】', '').strip()
    itx = it['text'].strip()
    if itx == jt:
        ok += 1
    elif jt.startswith(itx):
        mism.append((i, len(itx), len(jt), 'PREFIX'))
    elif itx.startswith(jt):
        mism.append((i, len(itx), len(jt), 'ITEM_LONGER'))
    else:
        mism.append((i, len(itx), len(jt), 'DIFF'))
out.append(f"identical={ok} mism={len(mism)}")
for m in mism[:20]:
    out.append(str(m))
# cand vs C
cok = 0
cm = []
for i, cb in enumerate(cand):
    ct = C[i].replace('【鈔】', '').strip() if i < len(C) else ''
    if cb['text'].strip() == ct:
        cok += 1
    elif ct.startswith(cb['text'].strip()):
        cm.append((i, len(cb['text']), len(ct), 'PREFIX'))
    else:
        cm.append((i, len(cb['text']), len(ct), 'DIFF'))
out.append(f"cand identical={cok} mism={len(cm)}")
for m in cm:
    out.append(str(m))
open(os.path.join(HERE, '_a024_chk.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:8]))
