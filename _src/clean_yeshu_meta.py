
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
O = os.path.join(D,'AI語譯','out','03_業疏')
S = os.path.join(D,'TXT_分卷','03_業疏')
drop = re.compile(r'(底本\s*[:：]|CBETA|大正藏|卍續藏|節自|節錄自|^=+\s*$|四分律刪補隨機羯磨疏[\u4e00-\u9fff]*\s*卷[一二三四]之[一二三四五六]（[^）]*）|四分律刪補隨機羯磨疏濟緣記卷[一二三四]之[一二三四五六]（續）)')
def clean_lines(text):
    out=[]
    for ln in text.split('\n'):
        if drop.search(ln) and len(ln) < 120: continue
        out.append(ln)
    return '\n'.join(out)
reps = [('自無答也','自無咎也'),('僧伽摩跋','僧伽跋摩'),('僧伽 摩䟦','僧伽跋摩'),
        ('[田*累]','螺'),('若作若作','若作'),('紗糓','紗縠'),('糓帛','縠帛'),
        ('名迦羅毗','名頞迦羅毗'),('不啻象鼻','無異於象鼻')]
n=0; files=0
for base in (O,S):
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'): continue
        p=os.path.join(base,f); t=io.open(p,encoding='utf-8').read(); b=t
        t=clean_lines(t)
        for a,c in reps: t=t.replace(a,c)
        t=re.sub(r'\n{3,}','\n\n',t)
        if t!=b:
            io.open(p,'w',encoding='utf-8').write(t); files+=1; n+=1
print('files changed', files)
