
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\docs'
toc={}
for book in sorted(os.listdir(D)):
    bd=os.path.join(D,book)
    if not os.path.isdir(bd) or book=='search': continue
    for f in sorted(os.listdir(bd)):
        if not f.endswith('.html'): continue
        t=io.open(os.path.join(bd,f),encoding='utf-8').read()
        m=re.search(r'<div class="subtoc">(.*?)</div>', t, re.S)
        if m:
            links=re.findall(r'<a href="#(p\d+)">([^<]+)</a>', m.group(1))
            if links: toc[(book,f[:-5])]=links
n=0
for book in sorted(os.listdir(D)):
    bd=os.path.join(D,book)
    if not os.path.isdir(bd) or book=='search': continue
    for f in sorted(os.listdir(bd)):
        if not f.endswith('.html'): continue
        p=os.path.join(bd,f); t=io.open(p,encoding='utf-8').read()
        if 'navsub' in t: continue
        changed=False
        for (bk,vol),links in toc.items():
            pat=re.compile(r'(<a href="(\.\./)?%s/%s\.html">)%s(</a>)' % (re.escape(bk), re.escape(vol), re.escape(vol)))
            if pat.search(t):
                def mk(m):
                    pre=m.group(2) or ''
                    sub='<div class="navsub">'+''.join('<a href="%s%s/%s.html#%s">%s</a>'%(pre,bk,vol,a,nm) for a,nm in links)+'</div>'
                    return m.group(1)+vol+m.group(3)+sub
                t=pat.sub(mk, t, count=1); changed=True
        if changed:
            io.open(p,'w',encoding='utf-8').write(t); n+=1
print('patched', n)
