import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '02_戒疏')
LAY = json.load(io.open(os.path.join(B, 'AI語譯', 'layers', '02_戒疏.json'), encoding='utf-8'))
LAB = {'律': '律', '註': '註', '疏': '疏', '記': '記'}
LEAD = re.compile(r'^【(律|註|疏|記)】')

n = 0
files = 0
for key, lay in LAY.items():
    p = os.path.join(S, key + '.txt')
    if not os.path.exists(p):
        continue
    raw = io.open(p, encoding='utf-8').read().split('\n')
    head, body = raw[:5], raw[5:]
    lines = [x for x in body if x.strip()]
    if len(lines) != len(lay):
        print('!! 段數不符', key, len(lines), len(lay))
        continue
    out = []
    changed = False
    for i, s in enumerate(lines):
        t = s.strip()
        m = LEAD.match(t)
        body_txt = LEAD.sub('', t).strip() if m else t
        L = lay[i]
        if L in LAB:
            new = '【' + LAB[L] + '】' + body_txt
        else:
            new = body_txt
        if new != t:
            changed = True
            n += 1
        out.append(new)
    if changed:
        io.open(p, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(out) + '\n')
        files += 1
print('source lines labelled', n, 'files', files)
