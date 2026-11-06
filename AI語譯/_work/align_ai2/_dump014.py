# -*- coding: utf-8 -*-
"""Dump full paragraphs around the align_ai2 batch 014 windows for inspection."""
import io
import os
import json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai2')
ZDIR = os.path.join(B, 'TXT_分卷', '資持記_細分')
CDIR = os.path.join(B, 'TXT_分卷', '01_行事鈔')


def load(d):
    out = []
    for f in sorted(os.listdir(d), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(d, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        out += sp
    return out


Z = load(ZDIR)
S = load(CDIR)
batch = json.load(io.open(os.path.join(AD, '014.json'), encoding='utf-8'))
items, cand = batch['items'], batch['cand']
print('Z total', len(Z), 'C total', len(S))

# 記 window: find z whose text starts with items[0] prefix
head0 = items[0]['text'][:14]
iz = next(i for i, p in enumerate(Z) if p.startswith(head0))
print('記 window at', iz, 'n', len(items))
# 鈔 window
hc0 = cand[0]['text'][:14]
ic = next(i for i, p in enumerate(S) if p.startswith(hc0))
print('鈔 window at', ic, 'n', len(cand))

with io.open(os.path.join(AD, '_dump014_z.txt'), 'w', encoding='utf-8') as fh:
    fh.write('=== 記 global z %d..%d ===\n' % (iz, iz + len(items) - 1))
    for k in range(max(0, iz - 3), min(len(Z), iz + len(items) + 3)):
        fh.write('[%d] %s\n\n' % (k, Z[k]))

with io.open(os.path.join(AD, '_dump014_c.txt'), 'w', encoding='utf-8') as fh:
    fh.write('=== 鈔 sections: idx26 諸雜要行 (window) ===\n')
    for k in range(ic, ic + len(cand)):
        fh.write('[c%d] %s\n\n' % (k - ic, S[k]))
    fh.write('\n=== following 3 篇 (should be the real counterpart) ===\n')
    for k in range(ic + len(cand), min(len(S), ic + len(cand) + 70)):
        fh.write('[%d] %s\n\n' % (k, S[k]))

print('ok')
