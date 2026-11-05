# -*- coding: utf-8 -*-
"""把 02_戒疏 中殘留的短標籤【律】【註】【疏】【記】補成四層標籤（依 layers.json）。"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LAB = {'律': '律文', '註': '註文', '疏': '疏文', '記': '記文'}
SHORT = re.compile(r'^【(律|註|疏|記)】')
LEAD = re.compile(r'^(【[^】]{1,6}】)+')

layers = json.load(io.open(os.path.join(B, 'AI語譯', 'layers', '02_戒疏.json'), encoding='utf-8'))
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')
n = 0
for key, lay in layers.items():
    p = os.path.join(T, key + '.txt')
    if not os.path.exists(p):
        continue
    ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    if len(ps) != len(lay):
        continue
    out = []
    changed = False
    for i, seg in enumerate(ps):
        body = seg
        while SHORT.match(body) or LEAD.match(body) and not SHORT.match(body):
            m = SHORT.match(body)
            if m:
                body = body[m.end():].strip()
                changed = True
                continue
            break
        if lay[i] in LAB:
            new = '【' + LAB[lay[i]] + '】' + body
        else:
            new = LEAD.sub('', body).strip()
        if changed and new != seg:
            n += 1
        out.append(new)
    if changed:
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
print('paras updated', n)
