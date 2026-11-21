# -*- coding: utf-8 -*-
"""建立與 TXT 漢字序列完全一致的句讀校定本。"""
import difflib, io, os, re, sys, time
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'TXT_句讀校定')
os.makedirs(OUT, exist_ok=True)
BOOKS = {
 'yeshu': ('TXT/03_四分律刪補隨機羯磨疏.txt', ['TXT_分卷_標點/03_業疏']),
 'nicao': ('TXT/04_四分律比丘尼鈔.txt', ['TXT_句讀/04_尼鈔']),
 'yichao': ('TXT/05_四分律拾毗尼義鈔.txt', ['TXT_分卷/05_拾毗尼義鈔_標點']),
}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
for book,(rawp,dirs) in BOOKS.items():
    raw = io.open(os.path.join(B,rawp),encoding='utf-8').read()
    punct = ''
    for d in dirs:
        D=os.path.join(B,d)
        for f in sorted(os.listdir(D)):
            if f.endswith('.txt'): punct += io.open(os.path.join(D,f),encoding='utf-8').read()
    ha=han(raw); hb=han(punct)
    # punctuation after each punct Han char
    after={}; last=0
    # build punct char positions of Han
    pos=[]
    for i,c in enumerate(punct):
        if '\u4e00'<=c<='\u9fff': pos.append(i)
    for j in range(len(pos)):
        end=pos[j+1] if j+1<len(pos) else len(punct)
        between=''.join(ch for ch in punct[pos[j]+1:end] if ch not in '\r\n')
        after[j]=between
    t=time.time()
    sm=difflib.SequenceMatcher(None,ha,hb,autojunk=False)
    blocks=sm.get_matching_blocks()
    mapping={}
    for a,b,n in blocks:
        for k in range(n): mapping[a+k]=b+k
    out=[]; hi=0
    for c in raw:
        if '\u4e00'<=c<='\u9fff':
            out.append(c)
            j=mapping.get(hi)
            if j is not None: out.append(after.get(j,''))
            hi+=1
        elif c=='\n':
            out.append('\n')
    text=''.join(out)
    # collapse excessive newlines
    text=re.sub(r'\n{3,}','\n\n',text)
    fp=os.path.join(OUT,book+'.txt')
    io.open(fp,'w',encoding='utf-8').write(text)
    matched=sum(n for _,_,n in blocks)
    print(book,'rawhan',len(ha),'puncthan',len(hb),'matched',matched,'ratio',round(matched/max(1,len(ha)),4),'sec',round(time.time()-t,1),'->',fp)
