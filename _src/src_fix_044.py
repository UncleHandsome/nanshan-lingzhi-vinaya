import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', 'out', '資持記', '06c_中一上.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
n = 0
for i, t in enumerate(tt[:-1]):
    k = t.find('戒淨障業')
    if k > 0:
        moved = t[k:]
        tt[i] = t[:k].rstrip()
        tt[i + 1] = moved.rstrip() + tt[i + 1]
        n += 1
        print('記043→044 移回，第', i + 1, '段')
        break
io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
print('done', n)
