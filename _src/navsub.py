
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\docs'
# 1. 收集各卷的篇目（來自先前加的 .subtoc）
toc = {}
for book in sorted(os.listdir(D)):
    bd=os.path.join(D,book)
    if not os.path.isdir(bd) or book=='search': continue
    for f in sorted(os.listdir(bd)):
        if not f.endswith('.html'): continue
        t=io.open(bd and os.path.join(bd,f),encoding='utf-8').read()
        m=re.search(r'<div class="subtoc">(.*?)</div>', t, re.S)
        if m:
            links=re.findall(r'<a href="#(p\d+)">([^<]+)</a>', m.group(1))
            if links: toc[(book,f[:-5])]=links
print('volumes with toc', len(toc))
# 2. 在每個頁面的側欄，為對應卷插入篇目
n=0
for book in sorted(os.listdir(D)):
    bd=os.path.join(D,book)
    if not os.path.isdir(bd) or book=='search': continue
    for f in sorted(os.listdir(bd)):
        if not f.endswith('.html'): continue
        p=os.path.join(bd,f); t=io.open(p,encoding='utf-8').read()
        if 'class="navsub"' in t: continue
        changed=False
        for (bk,vol),links in toc.items():
            href='%s/%s.html' % (bk, vol)
            needle='<a href="%s">' % href
            if needle in t and href in t:
                sub='<div class="navsub">' + ''.join('<a href="%s#%s">%s</a>'%(href,a,nm) for a,nm in links) + '</div>'
                t=t.replace(needle+vol+'</a>', needle+vol+'</a>'+sub, 1)
                changed=True
        if changed:
            io.open(p,'w',encoding='utf-8').write(t); n+=1
print('pages patched', n)
