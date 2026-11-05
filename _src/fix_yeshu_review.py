
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
O = os.path.join(D,'AI語譯','out','03_業疏')
reps = [
 ('這部《資持記》','這部《濟緣記》'),
 ('九百二十一億六萬歲','九百二十一億六千萬歲'),
 ('輪流宣說戒相','登上轉輪高座宣說戒相'),
 ('「不隱沒的無記性」','「不隱沒的無記性」（即無覆無記）'),
 ('在解界處立戒堂','開許解除戒堂'),
 ('橫向劈裂六道重重關卡','橫越生死重重險關'),
 ('兩種聲音分別呼召','以平聲與去聲兩種字音分別呼召'),
 ('觸碰推移僧眾的器物','用手指粗暴戳弄推擲僧團器物'),
 ('沒有確定日期','非每半月之常期'),
 ('未曾具足','屬簡化規格、未如白二那樣具足'),
]
tot = {}
for f in sorted(os.listdir(O)):
    if not f.endswith('.txt'): continue
    p = os.path.join(O,f); t = io.open(p,encoding='utf-8').read(); b=t
    for a,c in reps:
        if a in t:
            t=t.replace(a,c); tot[a]=tot.get(a,0)+1
    t = re.sub(r'\[段數不合[^\]]*\]','',t)
    if t!=b: io.open(p,'w',encoding='utf-8').write(t)
print('files changed', len(tot))
for k,v in tot.items(): print(v, k[:16])
