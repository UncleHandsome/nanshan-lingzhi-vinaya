
# -*- coding: utf-8 -*-
import io, re
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\out\02_戒疏\19b_卷四下之一.txt'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'[ \t]*\r?\n[ \t]*\r?\n[ \t]*(?:\r?\n[ \t]*)*', '\n\n', t)
arr = [x.strip() for x in t.split('\n\n') if x.strip()]
print('paras after normalize', len(arr))
while len(arr) < 140:
    i = max(range(len(arr)), key=lambda k: len(arr[k]))
    s = arr[i]; cut = s.find('。', max(20, len(s)//3))
    if cut < 0: break
    arr[i:i+1] = [s[:cut+1].strip(), s[cut+1:].strip()]
while len(arr) > 140:
    arr[0] = arr[0] + arr[1]; arr.pop(1)
io.open(p,'w',encoding='utf-8').write('\n\n'.join(arr))
print('final', len(arr))
