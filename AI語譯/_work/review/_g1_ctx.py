# -*- coding: utf-8 -*-
import json, re, collections

d = json.load(open('AI語譯/_work/review/_g1_data.json', encoding='utf-8'))


def strip_alt(t):
    # remove alternative parentheticals  （或：...） （或...）
    t2 = re.sub(r'（或[：:][^）]*）', '', t)
    t2 = re.sub(r'（或[^：:）][^）]*）', '', t2)
    return t2


def ctx(txt, s, t):
    i = txt.find(s)
    if i < 0:
        return ''
    a = max(0, i - 12)
    b = min(len(txt), i + len(s) + 12)
    return txt[a:i] + '【' + txt[i:i + len(s)] + '→' + t + '】' + txt[i + len(s):b]


out = open('AI語譯/_work/review/_g1_auto_ctx.txt', 'w', encoding='utf-8')
for x in d:
    if x['status'] != 'auto':
        continue
    cur = x['cur']
    for p in x['pairs']:
        src, tgt = p[0][0], strip_alt(p[1])
        out.write(x['gid'] + '\t' + ctx(cur, src, tgt) + '\n')
out.close()
print('done')
