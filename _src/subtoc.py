
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\docs'
PAT = re.compile(r'([\u4e00-\u9fff]{2,8}篇第[一二三四五六七八九十]+)')
total=0
for book in sorted(os.listdir(D)):
    bd=os.path.join(D,book)
    if not os.path.isdir(bd) or book in ('search',): continue
    for f in sorted(os.listdir(bd)):
        if not f.endswith('.html'): continue
        p=os.path.join(bd,f); t=io.open(p,encoding='utf-8').read()
        if 'class="subtoc"' in t: continue
        # 找篇名所在元素
        subs=[]
        def repl(m):
            name=m.group(1)
            if name in [n for n,_ in subs]: return m.group(0)
            subs.append((name,len(subs)))
            return m.group(0)
        for m in PAT.finditer(t):
            nm=m.group(1)
            if nm not in [n for n,_ in subs]:
                subs.append((nm,len(subs)))
        if not subs: continue
        # 為每個篇名在其所在的 div 加 id
        for nm,i in subs:
            idx=t.find(nm)
            if idx<0: continue
            start=t.rfind('<div', 0, idx)
            if start<0: continue
            t=t[:start]+t[start:].replace('<div','<div id="p%d"'%i,1)
        toc='<div class="subtoc">' + ''.join('<a href="#p%d">%s</a>'%(i,nm) for nm,i in subs) + '</div>'
        # 插在 main 開頭
        t=t.replace('<main>', '<main>'+toc, 1)
        io.open(p,'w',encoding='utf-8').write(t)
        total+=1
print('pages with subtoc', total)
