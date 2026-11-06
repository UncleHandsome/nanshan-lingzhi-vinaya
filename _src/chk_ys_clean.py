import io, sys, os, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import site_ju
vols = site_ju.get('03_業疏')
n = 0
for v, entries in vols:
    for o, t in entries:
        if '焉。**【記】' in o or '**【記】' in o:
            n += 1
            print(v, '|', o[:70])
print('命中', n)
