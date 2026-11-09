# -*- coding: utf-8 -*-
import json, difflib, sys

D = json.load(open('AI語譯/_work/review/_g1_data.json', encoding='utf-8'))
OUT = json.load(open('AI語譯/_work/review/_g1_out.json', encoding='utf-8'))

cur = {}
for r in D:
    cur.setdefault((r['chunk'], r['seg']), r['cur'])

manual = set(json.load(open('AI語譯/_work/review/_g1_mgids.json', encoding='utf-8')))
out = open('AI語譯/_work/review/_g1_manual_ctx.txt', 'w', encoding='utf-8')
for b, ch, sg, txt in OUT:
    old = cur[(ch, sg)]
    if old == txt:
        continue
    sm = difflib.SequenceMatcher(None, old, txt)
    parts = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        a = max(0, i1 - 18)
        bb = min(len(old), i2 + 18)
        parts.append(old[a:i1] + '【' + old[i1:i2] + '→' + txt[j1:j2] + '】' + old[i2:bb])
    gid0 = None
    for r in D:
        if (r['chunk'], r['seg']) == (ch, sg):
            gid0 = r['gid']
            break
    if gid0 in manual:
        out.write(gid0 + '\t' + ch + ' ' + sg + '\t' + ' /// '.join(parts) + '\n')
out.close()
print('ok')
