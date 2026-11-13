import sys,os
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\note_map\_scripts")
from align_lib import *
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
idx=NoteIndex(os.path.join(root,"TXT","資持記","06_中一上.txt"))
lines=read_lines(os.path.join(root,"TXT_分卷","01_行事鈔","05a_卷中之一.txt"))
ps=[l[2:] for l in lines if l.startswith("\u3000\u3000")]
def show(p,label):
    g=grams(norm(p))
    print(f"{label} len={len(p)} grams={len(g)} cover_full={len(g & grams(idx.text))/len(g):.3f}")
    print("   head:",p[:24])
p=ps[5]; show(p,"鈔01")
pos=idx.text.find("特須先示方顯後文")
print("pos 記018:",pos)
print("cover 0..pos:", round(len(grams(norm(p)) & grams(idx.text[:pos]))/len(grams(norm(p))),3))
for i in range(5,10): show(ps[i],f"P{i}")
