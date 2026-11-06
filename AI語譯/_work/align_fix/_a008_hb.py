# -*- coding: utf-8 -*-
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
h = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
print('keys', sorted(h.keys(), key=int))
a = h['13']
print('len', len(a), 'monotone', all(a[i] <= a[i+1] for i in range(len(a)-1)), 'max', max(a), 'min', min(a))
print('290..470:')
for i in range(285, min(len(a), 470)):
    print(i, a[i], end='  |  ')
print()
# compare with out_007
o7 = json.load(io.open(os.path.join(D, 'out_007.json'), encoding='utf-8'))['map']
m7 = {int(x['z']): int(x['c']) for x in o7}
print('out007 len', len(m7), 'range', min(m7), max(m7))
diff = [(z, m7[z], a[z]) for z in sorted(m7) if m7[z] != a[z]]
print('diff count', len(diff))
print(diff[:40])
