import sys,os
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\note_map\_scripts")
from align_lib import *
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
idx=NoteIndex(os.path.join(root,"TXT","資持記","06_中一上.txt"))
# 鈔01
lines=read_lines(os.path.join(root,"TXT_分卷","01_行事鈔","05a_卷中之一.txt"))
p=[l[2:] for l in lines if l.startswith("\u3000\u3000")][4]  # 5th P = 出俗五眾
g=grams(norm(p))
print("len",len(p),"grams",len(g))
print("cover full vol:", round(len(g & grams(idx.text))/len(g),3))
# span 記001-018前半: find where 記018 starts (text 特須先示)
pos=idx.text.find("特須先示方顯後文")
print("pos of 記018:",pos)
print("cover to pos:", round(len(g & grams(idx.text[:pos]))/len(g),3))
print("cover within pos+-2000:", round(len(g & grams(idx.text[max(0,pos-2200):pos]))/len(g),3))
