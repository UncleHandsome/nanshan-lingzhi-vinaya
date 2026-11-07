import io, os, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'untrans_filled.json'), encoding='utf-8-sig'))
out = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
files = os.listdir(out)
n = 0
for k, items in d.items():
    cand = [f for f in files if f.startswith(k) and f.endswith('.txt')]
    if not cand:
        print('缺檔', k)
        continue
    fp = os.path.join(out, cand[0])
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
    for idx, val in items.items():
        i = int(idx) - 1
        if 0 <= i < len(tt):
            tt[i] = str(val).strip()
            n += 1
    io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
    print(cand[0], len(items))
print('已寫回', n, '段')
