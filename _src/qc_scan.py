
# -*- coding: utf-8 -*-
import os, io, re, json
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

WEN = re.compile(r'[之乎者也矣焉哉爾云]')
def ratio_flag(a, b):
    if not a or not b: return None
    r = len(b)/len(a)
    if r < 0.55: return 'too_short'
    if r > 3.2: return 'too_long'
    if a == b: return 'identical'
    if len(b) > 40 and len(WEN.findall(b))/len(b) > 0.10 and len(WEN.findall(b))/len(b) >= len(WEN.findall(a))/max(1,len(a))*0.8:
        return 'wenyan'
    return None

for tag in ['02_戒疏','04_比丘尼鈔','03_業疏','01_行事鈔']:
    cnt = {}; samples = []
    for key, sp, tp in load(tag):
        n = min(len(sp), len(tp))
        for i in range(n):
            f = ratio_flag(sp[i], tp[i])
            if f:
                cnt[f] = cnt.get(f,0)+1
                if len(samples) < 5: samples.append((key,i,f,tp[i][:50]))
    print(tag, cnt)
    for s in samples: print('   ', s[0], s[1], s[2], s[3])
