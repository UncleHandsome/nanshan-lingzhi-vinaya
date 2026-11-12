# -*- coding: utf-8 -*-
"""setrow.py NNN fixed rej [doubt] [note] -- 更新 r3_done.tsv 中該 nnn 的列。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
P = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\r3_done.tsv'
nnn, fixed, rej = sys.argv[1], sys.argv[2], sys.argv[3]
doubt = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
note = sys.argv[5] if len(sys.argv) > 5 else None
rows = [l.rstrip('\n') for l in open(P, encoding='utf-8') if l.strip()]
out, hit = [], 0
for ln in rows:
    p = ln.split('\t')
    if p[0] == nnn and len(p) >= 6:
        p[2] = fixed
        p[3] = rej
        if doubt is not None:
            p[4] = doubt
        if note:
            p[5] = note
        ln = '\t'.join(p)
        hit += 1
    out.append(ln)
open(P, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('updated', hit, 'row(s) for', nnn)
