import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
names = ['諸戒受法篇第三', '諸眾安居法篇第六', '諸眾自恣法篇第七', '懺六聚法篇第九',
         '衣藥受淨篇第四', '諸說戒法篇第五', '諸分衣法篇第八', '雜法住持篇第十']
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    for i, p in enumerate(sp, 1):
        for n in names:
            if n in p:
                print('%-14s #%-3d %-10s | %s' % (f[:-4], i, n, p[:48]))
