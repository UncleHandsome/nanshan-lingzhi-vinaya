
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(D,'AI語譯','out','05_拾毗尼義鈔')
reps = [('元照律師解釋','智首律師解釋'),('元照律師（首解）','智首律師（首解）'),
        ('《大毗婆沙論》','《薩婆多論》'),('大毗婆沙論','薩婆多論'),
        ('強說粗惡語','強敷坐臥具'),('去歲會昌五年','往昔會昌五年'),
        ('十一條戒的本體','十條戒的本體')]
n=0
for f in sorted(os.listdir(d)):
    if not f.endswith('.txt'): continue
    p=os.path.join(d,f); t=io.open(p,encoding='utf-8').read(); b=t
    for a,c in reps: t=t.replace(a,c)
    if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
print('files',n)
