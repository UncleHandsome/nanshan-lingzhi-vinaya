import io, re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, B + r'\_src')
import site_ju
pairs = site_ju.pairs_chunks('03_業疏', '03_業疏', '03_業疏')
names = ['諸戒受法篇第三', '諸眾安居法篇第六', '諸眾自恣法篇第七', '懺六聚法篇第九', '諸說戒法篇第五']
for vol, entries in pairs:
    for i, (o, t) in enumerate(entries):
        for n in names:
            if n in o:
                pos = o.find(n)
                print('%s #%d %s | pos=%d len=%d | %s' % (vol, i, n, pos, len(o), o[:50]))
