
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B,'TXT_分卷','01_行事鈔'); T = os.path.join(B,'AI語譯','out','01_行事鈔')
pat = re.compile(r'^\d+\s+.*篇\([上中下][一二三四]\)$')
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt') or f.startswith('00_'): continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip() and not pat.match(x.strip())]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip() and not pat.match(x.strip())]
    if len(sp) != len(tp): print(key, len(sp), len(tp))
