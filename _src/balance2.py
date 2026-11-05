
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
targets = [('02_戒疏','18b_卷四上之三',146),('02_戒疏','19b_卷四下之一',120)]
def split_longest(arr):
    i = max(range(len(arr)), key=lambda k: len(arr[k]))
    s = arr[i]; cut = s.find('。', len(s)//2)
    if cut < 0: cut = len(s)//2
    arr[i:i+1] = [s[:cut+1], s[cut+1:]]
    return arr
def merge_shortest(arr):
    i = min((k for k in range(1, len(arr))), key=lambda k: len(arr[k]))
    arr[i-1] += arr[i]; arr.pop(i); return arr
for tag,key,want in targets:
    p=os.path.join(D,'AI語譯','out',tag,key+'.txt')
    raw=io.open(p,encoding='utf-8').read()
    sep='\r\n\r\n' if '\r\n\r\n' in raw else '\n\n'
    arr=[x for x in re.split(r'\r?\n\r?\n', raw) if x.strip()]
    n0=len(arr)
    while len(arr)<want: arr=split_longest(arr)
    while len(arr)>want: arr=merge_shortest(arr)
    io.open(p,'w',encoding='utf-8').write(sep.join(arr))
    print(key, n0,'->',len(arr))
