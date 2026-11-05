
# -*- coding: utf-8 -*-
import io, os, re, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
BOOKDIR = {'01_行事鈔':'01_行事鈔','03_業疏':'03_業疏','02_戒疏':'02_戒疏','資持記':'資持記','04_比丘尼鈔':'04_比丘尼鈔','05_拾毗尼義鈔':'05_拾毗尼義鈔'}
pairs = re.compile(r'[「『]([^」』]{2,40})[」』]\s*(?:改為|改作|應作|當作|作)\s*[「『]([^」』]{1,60})[」』]')
applied=0; skipped=0; files=0
for f in sorted(os.listdir(RV)):
    if not f.endswith('.json'): continue
    book, key = f[:-5].split('__',1)
    if book not in BOOKDIR: continue
    p = os.path.join(D,'AI語譯','out',book,key+'.txt')
    if not os.path.exists(p): continue
    t = io.open(p, encoding='utf-8').read()
    issues = json.load(io.open(os.path.join(RV,f), encoding='utf-8'))
    changed=False
    for it in issues:
        txt = (it.get('fix') or '') + ' ' + (it.get('issue') or '')
        for m in pairs.finditer(txt):
            a, b = m.group(1), m.group(2)
            if a == b: continue
            c = t.count(a)
            if c == 1:
                t = t.replace(a, b); applied += 1; changed=True
            else:
                skipped += 1
    if changed:
        io.open(p,'w',encoding='utf-8').write(t); files+=1
print('applied', applied, 'skipped', skipped, 'files', files)
