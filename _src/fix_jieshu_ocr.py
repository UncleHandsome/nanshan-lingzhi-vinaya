
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
reps = [
 ('弓失','弓矢'),('明且以示','明旦以示'),('糟醫','糟醷'),('大戲形望','大虧形望'),
 ('無心壓背','無心厭背'),('問之，何呵責','問之，彼呵責'),('難䟦 陀','跋難陀'),
 ('難䟦陀','跋難陀'),('難䟦 䟦 陀','跋難陀'),('初示丸搩','初示九搩'),('披逸提','波逸提'),
 ('後不億','後不憶'),('不億是妄語','不憶是妄語'),('酉南夷','西南夷'),('刀兵灾起','刀兵災起'),
 ('劒戟','劍戟'),('無耻','無恥'),('遲緩之皃','遲緩之貌'),('須𢷤 𢷤','須擯'),('故須 也','故須擯也'),
 ('與利涉',''),('失失正念','失卻正念'),
 ('應讀為平聲（指過失、超越）','應讀為平聲（意為「超過、踰越」）'),
 ('索求供養利養','索求供養利養'),
]
for sub in ('TXT_分卷','AI語譯'):
    base = os.path.join(D, sub, '02_戒疏') if sub=='TXT_分卷' else os.path.join(D,'AI語譯','out','02_戒疏')
    if not os.path.isdir(base): continue
    n=0
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'): continue
        p=os.path.join(base,f); t=io.open(p,encoding='utf-8').read(); b=t
        for a,c in reps: t=t.replace(a,c)
        if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
    print(sub,'files',n)
