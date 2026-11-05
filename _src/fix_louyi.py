
# -*- coding: utf-8 -*-
import io, os, json, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
def clean(s):
    s = (s or '').strip()
    s = re.sub(r'^(應譯為|可譯為|宜譯為|譯為|改譯為|應改為|改為|補譯為)[：:]?', '', s).strip()
    return s.strip('「」『』')
tot = {}
for f in sorted(os.listdir(RV)):
    if not f.endswith('.json'): continue
    book, key = f[:-5].split('__',1)
    p = os.path.join(D,'AI語譯','out',book,key+'.txt')
    if not os.path.exists(p): continue
    arr = json.load(io.open(os.path.join(RV,f), encoding='utf-8'))
    t = io.open(p, encoding='utf-8').read(); n=0
    for it in arr:
        if '漏譯' not in (it.get('kind') or ''): continue
        q = (it.get('quote') or '').strip(); fx = clean(it.get('fix'))
        if not q or not fx or len(fx) < 10: continue
        if q in t:
            t = t.replace(q, fx, 1); n += 1
    if n:
        io.open(p,'w',encoding='utf-8').write(t)
        tot[book] = tot.get(book,0)+n
print(json.dumps(tot, ensure_ascii=False), 'total', sum(tot.values()))
