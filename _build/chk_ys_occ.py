import io, re, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, B + r'\_src')
import site_ju
pairs = site_ju.pairs_chunks('03_業疏', '03_業疏', '03_業疏')
for vol, entries in pairs:
    if vol != '卷一':
        continue
    for i, (o, t) in enumerate(entries):
        if '集法緣成篇第一' in o:
            print(i, '|', o[:60])
