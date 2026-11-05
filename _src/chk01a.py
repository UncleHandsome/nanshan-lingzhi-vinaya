
import os, io, re
BASE = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(BASE, 'TXT_分卷', '01_行事鈔')
TR = os.path.join(BASE, 'AI語譯', 'out', '01_行事鈔')
pat = re.compile(r'^\d+\s+.*篇\([上中下][一二三四]\)$')
for f in sorted(os.listdir(SRC)):
    if not f.startswith('01a'): continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(SRC,f),encoding='utf-8').read().split('\n')[5:] if x.strip() and not pat.match(x.strip())]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(TR,key+'.txt'),encoding='utf-8').read()) if x.strip()]
    print('src', len(sp), 'tr', len(tp))
    for i in range(10, 16):
        print(' SRC', i, sp[i][:30] if i < len(sp) else '-')
        print(' TR ', i, tp[i][:30] if i < len(tp) else '-')
