# -*- coding: utf-8 -*-
"""Work dump for batch 005: full 記 sec13 paragraphs and 鈔 c0..c6."""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')


def load(sub):
    S = os.path.join(B, 'TXT_分卷', sub)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        for ln in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:]:
            ln = ln.strip()
            if ln:
                out.append((f, ln))
    return out


Z = load('資持記_細分')
S = load('01_行事鈔')
d = json.load(io.open(os.path.join(AD, '005.json'), encoding='utf-8'))

# find 記 section 13 start and sec 14 start
z0 = next(i for i, (f, p) in enumerate(Z) if p.startswith('又上三中，前二隨文'))
z1 = next(i for i, (f, p) in enumerate(Z) if i > z0 and '14 釋釋相篇' in p)
out = io.StringIO()
out.write('記 sec13 paragraphs: idx %d .. %d  (n=%d)\n' % (z0, z1 - 1, z1 - z0))
out.write('batched items = %d\n\n' % len(d['items']))
for i in range(z0, min(z1, z0 + 24)):
    mark = 'ITEM z%d' % (i - z0) if (i - z0) < len(d['items']) else '  (not in batch)'
    out.write('--- [%d] %s ---\n%s\n\n' % (i - z0, mark, Z[i][1]))

# 鈔 cand paragraphs (full text)
out.write('\n\n===== 鈔 cand (full paragraphs) =====\n')
# locate cand paragraphs
last = -1
for c in d['cand'][:8]:
    key = c['text'][:16]
    for i in range(last + 1, len(S)):
        if S[i][1].startswith(key):
            last = i
            out.write('--- c%d @%d ---\n%s\n\n' % (c['c'], i, S[i][1]))
            break
io.open(os.path.join(AD, '_w005.txt'), 'w', encoding='utf-8').write(out.getvalue())
print('ok')
