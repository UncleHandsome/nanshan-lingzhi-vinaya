# -*- coding: utf-8 -*-
import json, re

np = json.load(open('AI語譯/_work/review/_g1_np.json', encoding='utf-8'))


def strip_alt(t):
    t = re.sub(r'（或[：:][^）]*）', '', t)
    t = re.sub(r'（或[^：:）][^）]*）', '', t)
    return t


out = open('AI語譯/_work/review/_g1_np_ctx.txt', 'w', encoding='utf-8')
for x in np:
    if not x['np']:
        continue
    for a, b in x['np']:
        i = x['cur'].find(a)
        if i < 0:
            out.write(x['gid'] + '\tNOTFOUND\t' + a + ' => ' + b + '\n')
            continue
        b2 = strip_alt(b)
        s = max(0, i - 14)
        e = min(len(x['cur']), i + len(a) + 14)
        out.write(x['gid'] + '\t' + x['cur'][s:i] + '【' + a + '→' + b2 + '】' + x['cur'][i + len(a):e] + '\n')
out.close()
print('ok')
