
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
targets=[('02_戒疏','18b_卷四上之三','18b'),('02_戒疏','19b_卷四下之一','19b')]
def split_longest(a):
    i=max(range(len(a)),key=lambda k:len(a[k])); s=a[i]; c=s.find('。',len(s)//2)
    if c<0:c=len(s)//2
    a[i:i+1]=[s[:c+1],s[c+1:]]; return a
def merge_shortest(a):
    i=min((k for k in range(1,len(a))),key=lambda k:len(a[k])); a[i-1]+=a[i]; a.pop(i); return a
for tag,key,_ in targets:
    S=os.path.join(D,'TXT_分卷',tag,'%s.txt'%key)
    spL=len([x for x in io.open(S,encoding='utf-8').read().split('\n')[5:] if x.strip()])
    p=os.path.join(D,'AI語譯','out',tag,key+'.txt')
    raw=io.open(p,encoding='utf-8').read(); sep='\r\n\r\n' if '\r\n\r\n' in raw else '\n\n'
    arr=[x for x in re.split(r'\r?\n\r?\n',raw) if x.strip()]
    while len(arr)<spL: arr=split_longest(arr)
    while len(arr)>spL: arr=merge_shortest(arr)
    io.open(p,'w',encoding='utf-8').write(sep.join(arr))
    print(key,len(arr),'== src',spL)
