
# -*- coding: utf-8 -*-
import io, os, json, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
def clean(s):
    s = (s or '').strip()
    s = re.sub(r'^(應譯為|可譯為|宜譯為|譯為|改譯為|應改為|改為)[：:]?', '', s).strip()
    s = s.strip('「」『』')
    return s
targets = ['資持記__02e_上一下.json']
for f in targets:
    book, key = f[:-5].split('__',1)
    p = os.path.join(D,'AI語譯','out',book,key+'.txt')
    t = io.open(p, encoding='utf-8').read()
    arr = json.load(io.open(os.path.join(RV,f), encoding='utf-8'))
    n = 0
    for it in arr:
        q = (it.get('quote') or '').strip()
        fx = clean(it.get('fix'))
        if not q or not fx: continue
        if q in t:
            t = t.replace(q, fx); n += 1
        else:
            # 用前 20 字找
            head = q[:20]
            if len(head) >= 8 and head in t:
                i = t.index(head)
                # 找該句結尾（句號或段末）
                j = t.find('。', i)
                if j < 0: j = len(t)
                t = t[:i] + fx + t[j+1:]
                n += 1
    io.open(p,'w',encoding='utf-8').write(t)
    print(f, 'replaced', n, 'of', len(arr))
