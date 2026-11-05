
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
dir = os.path.join(D,'AI語譯','out','04_比丘尼鈔')
reps = [('《僧祇律》等十五部律典','《僧祇律》、《十誦律》、《五分律》等'),
        ('六千萬歲','六萬歲'),('四千萬歲','四萬歲'),('五千萬歲','五萬歲'),
        ('五千萬年','五萬年'),
        ('不共的殊勝因緣','共同普遍因緣（無差別通因）'),
        ('受缽篇第十四','受缽篇第十三'),
        ('第五是僧鬘物','第四是現前僧物（原文脫漏，據律制補）；第五是僧鬘物')]
n=0
for f in sorted(os.listdir(dir)):
    if not f.endswith('.txt'): continue
    p=os.path.join(dir,f); t=io.open(p,encoding='utf-8').read(); b=t
    for a,c in reps: t=t.replace(a,c)
    if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
print('files',n)
