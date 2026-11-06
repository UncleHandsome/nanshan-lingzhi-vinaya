# -*- coding: utf-8 -*-
import io, os, re, json
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai')
out = []
for f in sorted(os.listdir(AD)):
    if not re.match(r'^\d{3}\.json$', f):
        continue
    n = f[:3]
    d = json.load(io.open(os.path.join(AD, f), encoding='utf-8'))
    it, ca = d['items'], d['cand']
    op = os.path.join(AD, 'out_%s.json' % n)
    s = f"{n} sec={d.get('sec')} name={d.get('name')} items={len(it)} z={it[0]['z']}..{it[-1]['z']} cand={len(ca)} c={ca[0]['c']}..{ca[-1]['c']}"
    if os.path.exists(op):
        m = json.load(io.open(op, encoding='utf-8'))['map']
        cs = [x['c'] for x in m]
        mono = all(cs[i] <= cs[i+1] for i in range(len(cs)-1))
        s += f" | OUT n={len(m)} c={cs[0]}..{cs[-1]} distinct={len(set(cs))} mono={mono} inCand={all(c in [x['c'] for x in ca] for c in cs)}"
    out.append(s)
io.open(os.path.join(AD, '_tmp_all.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
