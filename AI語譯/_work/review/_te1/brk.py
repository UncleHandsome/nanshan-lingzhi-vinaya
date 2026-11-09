# -*- coding: utf-8 -*-
import glob, io
c1 = c2 = 0
ex1, ex2 = [], []
for p in glob.glob(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out\**\*.txt', recursive=True):
    t = io.open(p, encoding='utf-8').read()
    c1 += t.count('〕。')
    c2 += t.count('。〕')
    if '。〕' in t and len(ex2) < 3:
        i = t.find('。〕')
        ex2.append((p, t[max(0, i-40):i+10]))
    if '〕。' in t and len(ex1) < 2:
        i = t.find('〕。')
        ex1.append((p, t[max(0, i-30):i+5]))
out = ['count ]]. = %d   .]. = %d' % (c1, c2)]
for e in ex1:
    out.append('A %s :: %s' % e)
for e in ex2:
    out.append('B %s :: %s' % e)
io.open(r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1\_brk.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
