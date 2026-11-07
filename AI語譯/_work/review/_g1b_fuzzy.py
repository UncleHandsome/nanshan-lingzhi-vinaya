# -*- coding: utf-8 -*-
import io, os, re, json, difflib

REV = os.path.dirname(os.path.abspath(__file__))
res = json.load(io.open(os.path.join(REV, '_g1b_sel.json'), encoding='utf-8'))
fixed = set([7,8,9,17,18,19,21,22,23,24,25,26,27,32,33,35,36,37,39,41,46,47,48,49,50,51])

def quotes(s):
    out = []
    for m in re.finditer(r'「([^」]{4,300})」', s):
        out.append(m.group(1))
    for m in re.finditer(r'『([^』]{4,300})』', s):
        out.append(m.group(1))
    return out

w = io.open(os.path.join(REV, '_g1b_fuzzy.txt'), 'w', encoding='utf-8')
for i, x in enumerate(res, 1):
    if i in fixed:
        continue
    cur = x['out_para'] or ''
    qs = [q for q in quotes(x['problem']) + quotes(x['suggestion']) if len(q) >= 8]
    best = None
    for q in qs:
        n = len(q)
        for st in range(0, max(1, len(cur) - n + 1), 2):
            win = cur[st:st+n]
            r = difflib.SequenceMatcher(None, q, win).ratio()
            if best is None or r > best[0]:
                best = (r, q, win)
    if best:
        w.write('%2d %-12s seg=%-4s best=%.3f\n  Q: %s\n  W: %s\n' % (i, x['chunk'], x['seg'], best[0], best[1][:90], best[2][:90]))
w.close()
print('ok')
