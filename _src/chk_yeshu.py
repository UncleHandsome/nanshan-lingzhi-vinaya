
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B,'TXT_分卷','03_業疏'); T = os.path.join(B,'AI語譯','out','03_業疏')
bad = []
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'): continue
    key = f[:-4]
    sp = [x for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = [x for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip()]
    if len(sp) != len(tp): bad.append((key, len(sp), len(tp)))
print('chunks', len([f for f in os.listdir(S) if f.endswith('.txt')]), 'mismatch', len(bad))
for b in bad: print(b)
