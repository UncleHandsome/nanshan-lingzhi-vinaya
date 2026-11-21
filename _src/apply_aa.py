# -*- coding: utf-8 -*-
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AA = os.path.join(B, '重作材料_長段', 'aa.txt')
BOOKS = {
 '戒疏': ('jieshu', '戒疏', 'TXT/02_四分律含注戒本疏.txt'),
 '業疏': ('yeshu', '業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt'),
}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', str(s)))
t = io.open(AA, encoding='utf-8').read()
for name, (book, label, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read(); h=''; mp=[]
    for i,c in enumerate(raw):
        if '\u4e00'<=c<='\u9fff': h+=c; mp.append(i)
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows=[json.loads(x) for x in io.open(p,encoding='utf-8') if x.strip()]
    cover=[0]*len(h)
    for r in rows:
        a,b=r.get('raw_start',-1),r.get('raw_end',-1)
        if a>=0 and b>a:
            for i in range(a,min(b,len(h))): cover[i]+=1
    pat=re.compile(r'^## %s-G(\d+)\s*\n(.*?)(?=^## %s-G|\Z)'%(name,name),re.M|re.S)
    added=0
    for m in pat.finditer(t):
        blocks=[x.strip() for x in re.split(r'\n\s*\n',m.group(2)) if x.strip()]
        srcs=[]; trs=[]
        for b in blocks:
            if any(x in b for x in ('此處僅存','正文尚未展開','為缺口截斷處')):
                continue
            clean=re.sub(r'^(?:【[^】]+】\s*)+','',b).strip()
            th=han(clean)
            if not th: continue
            if h.find(th[:20])>=0 or h.find(th[:12])>=0:
                srcs.append(clean)
            else:
                trs.append(clean)
        if not srcs or not trs: continue
        src='\n'.join(srcs)
        src=re.sub(r'【[^】]+】\s*$','',src).strip()
        sh=han(src)
        q=h.find(sh[:20])
        if q<0: q=h.find(sh[:12])
        if q<0: continue
        e=q+len(sh)
        # 只補完全未覆蓋的缺口
        if any(cover[i] for i in range(q,min(e,len(h)))): continue
        tr='\n'.join(trs)
        rows.append({'book':label,'book_id':book,'key':'AA-'+name+'-G%02d'%int(m.group(1)),
                     'label':'疏文','source':src,'translation':tr,'revised':True,
                     'segments':[{'label':'疏文','source':src,'translation':tr}],
                     'raw_start':q,'raw_end':e,'vol':'','chunk':''})
        for i in range(q,min(e,len(h))): cover[i]+=1
        added+=1
    io.open(p,'w',encoding='utf-8').writelines(json.dumps(x,ensure_ascii=False)+'\n' for x in rows)
    print(name,'added',added,'rows',len(rows))
