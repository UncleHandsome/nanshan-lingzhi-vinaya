import os,sys,json
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
sys.path.insert(0,r"AI語譯\_work")
from edits import EDITS
files={}
def load(book,chunk):
    k=(book,chunk)
    if k not in files:
        p=os.path.join("AI語譯","out",book,chunk+".txt")
        raw=open(p,encoding="utf-8",newline="").read()
        files[k]=[raw.split("\n"),raw]
    return files[k]
for (book,chunk,para,old,new,key,src,note) in EDITS:
    L,_=load(book,chunk); i=2*para-2; line=L[i]; cn=line.rstrip("\r")
    assert cn.count(old)==1,(key,old)
    L[i]=cn.replace(old,new,1)
seen=[]
for (book,chunk,para,*rest) in EDITS:
    if (book,chunk,para) not in seen: seen.append((book,chunk,para))
for (book,chunk,para) in seen:
    L,_=load(book,chunk)
    print(f'=== {book}/{chunk}#{para}')
    print(L[2*para-2].rstrip("\r"))
    print()
