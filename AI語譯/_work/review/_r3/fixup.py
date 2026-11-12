# -*- coding: utf-8 -*-
"""fixup.py -- 修正 r3_done.tsv 現有列（077 fixed 3->4）並檢查 061-180 完整性。"""
import sys, collections
sys.stdout.reconfigure(encoding='utf-8')
P = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\r3_done.tsv'
rows = [l.rstrip('\n') for l in open(P, encoding='utf-8') if l.strip()]
out, seen = [], collections.Counter()
for ln in rows:
    p = ln.split('\t')
    if p[0] == '077' and len(p) >= 6 and p[2] == '3' and p[1] == '44':
        p[2] = '4'; p[3] = '40'
        ln = '\t'.join(p)
    out.append(ln)
    seen[p[0]] += 1
open(P, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
have = set(seen)
miss = [f'{i:03d}' for i in range(61, 181) if f'{i:03d}' not in have]
dups = sorted(k for k, v in seen.items() if v > 1)
print('rows', len(out), 'missing 061-180:', miss, 'dups:', dups)
