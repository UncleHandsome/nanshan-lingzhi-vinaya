import io, re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, B + r'\_src')
import site_ju
pairs = site_ju.pairs_chunks('03_業疏', '03_業疏', '03_業疏')
for vol, entries in pairs:
    if vol != '卷一':
        continue
    for i in [6, 7, 8, 411]:
        o, t = entries[i]
        print('---', i)
        print('O:', o[:80])
        print('T:', t[:80])
