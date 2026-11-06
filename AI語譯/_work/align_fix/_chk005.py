# -*- coding: utf-8 -*-
"""Sanity check: n-gram overlap between each 記 item and each 鈔 cand."""
import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(B, '005.json'), encoding='utf-8'))
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def grams(s, n):
    s = han(s)
    return set(s[i:i + n] for i in range(len(s) - n + 1))


C = [(c['c'], c['text']) for c in d['cand']]
out = []
for it in d['items']:
    scores = []
    for c, t in C:
        sc = 0
        for n in (2, 3, 4):
            sc += len(grams(it['text'], n) & grams(t, n)) * (n - 1)
        scores.append((sc, c))
    scores.sort(reverse=True)
    # longest common substring with each cand
    hz = han(it['text'])
    best_lcs = []
    for c, t in C:
        hc = han(t)
        bl = 0
        for i in range(len(hz)):
            for j in range(i + 3, min(len(hz), i + 12) + 1):
                if hz[i:j] in hc:
                    bl = max(bl, j - i)
        best_lcs.append((bl, c))
    best_lcs.sort(reverse=True)
    out.append('z=%-3d top3(gram)=%s  top3(lcs)=%s' % (it['z'], scores[:3], best_lcs[:3]))
io.open(os.path.join(B, '_chk005.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
