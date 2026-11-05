
import os, io, re, glob
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B,'TXT_分卷','01_行事鈔'); T = os.path.join(B,'AI語譯','out','01_行事鈔')
pat = re.compile(r'^\d+\s+.*篇\([上中下][一二三四]\)$')
bad = []
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt') or f.startswith('00_'): continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip() and not pat.match(x.strip())]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip() and not pat.match(x.strip())]
    jp = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[\u4e00-\u9fff]+$')
    i = 0
    while i < len(sp) and not jp.match(sp[i]): i += 1
    j = i
    while j < len(sp) and jp.match(sp[j]): j += 1
    if j - i >= 3 and j < len(sp):
        del sp[i:j]
    if len(sp) != len(tp): bad.append((key, len(sp), len(tp)))
print('mismatch chunks:', len(bad))
for b in bad: print(b)
for f in glob.glob(os.path.join(B,'白話','*.png')): os.remove(f)
print('cleaned png')
