import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
keys = ['01a_卷一之一', '01b_卷一之一', '17a_卷三之六', '17b_卷三之六']
out = {}
for k in keys:
    sp = [x.strip() for x in io.open(os.path.join(S, k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    out[k] = sp
p = os.path.join(B, 'AI語譯', '_work', 'ys_punct_in.json')
json.dump(out, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()}, '→', p)
