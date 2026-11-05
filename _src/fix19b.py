
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(D,'AI語譯','out','02_戒疏','19b_卷四下之一.txt')
raw = io.open(p, encoding='utf-8').read()
arr = [x.strip() for x in re.split(r'\r?\n\s*\r?\n', raw) if x.strip()]
print('paras', len(arr))
while len(arr) < 140:
    i = max(range(len(arr)), key=lambda k: len(arr[k]))
    s = arr[i]
    cut = s.find('。', max(20, len(s)//3))
    if cut < 0: break
    arr[i:i+1] = [s[:cut+1].strip(), s[cut+1:].strip()]
io.open(p,'w',encoding='utf-8').write('\r\n\r\n'.join(arr))
print('now', len(arr))
