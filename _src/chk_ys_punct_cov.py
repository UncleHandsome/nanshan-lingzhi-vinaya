import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
punct = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json'), encoding='utf-8'))
gi = 0
low = []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    seg = punct[gi:gi + len(sp)]
    gi += len(sp)
    ok = sum(1 for x in seg if re.search(r'[，。、；：？！]', x))
    if len(sp) and ok / len(sp) < 0.8:
        low.append((key, len(sp), ok))
print('低標點分塊：')
for x in low:
    print('  %-14s 段%4d 有標點%4d' % x)
print('總段', gi, '低於80%分塊', len(low))
