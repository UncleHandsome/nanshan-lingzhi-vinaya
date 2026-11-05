
# -*- coding: utf-8 -*-
import os, io, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def load(tag):
    S = os.path.join(B,'TXT_分卷',tag); T = os.path.join(B,'AI語譯','out',tag)
    out = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]; p = os.path.join(T, key+'.txt')
        if not os.path.exists(p): continue
        sp = [x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p,encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tp))
    return out
WEN = re.compile(r'[之乎者也矣焉哉]')
for tag in ['02_戒疏','04_比丘尼鈔','03_業疏']:
    short = long_ = wen = ident = 0; samples = []
    for key, sp, tp in load(tag):
        for i in range(min(len(sp), len(tp))):
            o, t = sp[i], tp[i]
            if len(o) < 40: continue
            if o == t: ident += 1
            if len(t) < 0.5*len(o): short += 1; samples.append(('短', key, i, o[:40], t[:40]))
            elif len(t) > 2.6*len(o): long_ += 1
            elif len(WEN.findall(t))/len(t) > 0.12: wen += 1; samples.append(('文', key, i, o[:40], t[:40]))
    print(tag, 'short', short, 'long', long_, 'wenyan', wen, 'identical', ident)
    for s in samples[:4]: print('   ', s)
