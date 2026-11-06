import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TR = os.path.join(B, 'AI語譯', '_work', 'xsc_juanshou_tr.json')
SRC = os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt')
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt')

d = json.load(io.open(TR, encoding='utf-8-sig'))
items = sorted(d.get('items', []), key=lambda x: x['i'])
sp = [x.strip() for x in io.open(SRC, encoding='utf-8').read().split('\n')[5:] if x.strip()]
print('原文', len(sp), '譯文', len(items))
tr = [''] * len(sp)
for it in items:
    if 0 <= it['i'] < len(sp):
        tr[it['i']] = it['t'].strip()
missing = [i for i, t in enumerate(tr) if not t]
print('缺譯', len(missing), missing[:5])
if missing:
    for i in missing:
        tr[i] = sp[i]          # 保底：沿用原文
io.open(OUT, 'w', encoding='utf-8').write('\n\n'.join(tr) + '\n')
print('寫入', OUT)
