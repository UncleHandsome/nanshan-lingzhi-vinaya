# -*- coding: utf-8 -*-
"""source 無句讀但 raw 切片有句讀時，改用 raw 切片（漢字相同才換）。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
 'xingshichao': 'TXT/01_四分律刪繁補闕行事鈔.txt',
 'yeshu': 'TXT/03_四分律刪補隨機羯磨疏.txt',
 'nicao': 'TXT/04_四分律比丘尼鈔.txt',
 'yichao': 'TXT/05_四分律拾毗尼義鈔.txt',
}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', str(s)))
for book, rawp in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read(); h=''; mp=[]
    for i,c in enumerate(raw):
        if '\u4e00'<=c<='\u9fff': h+=c; mp.append(i)
    p=os.path.join(B,'定稿',book+'.jsonl')
    rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
    fixed=0
    for r in rows:
        a,b=r.get('raw_start',-1),r.get('raw_end',-1)
        if a<0 or b<=a: continue
        s=r.get('source',''); n=len(re.findall(r'[\u4e00-\u9fff]',s))
        if n<=30 or re.search(r'[，。；：！？、]',s): continue
        if han(s)!=h[a:b]: continue
        rs=raw[mp[a]:mp[b-1]+1].strip()
        if re.search(r'[，。；：！？、]',rs):
            r['source']=rs
            for seg in r.get('segments') or []:
                if han(seg.get('source',''))==han(s):
                    seg['source']=rs
                    break
            fixed+=1
    io.open(p,'w',encoding='utf-8').writelines(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
    print(book,'fixed',fixed)
