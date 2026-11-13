import os
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p=os.path.join(root,"TXT_分卷_標點","03_業疏","02a_卷一之二.txt")
lines=open(p,encoding="utf-8").read().splitlines()
for i,l in enumerate(lines[:12],1): print(i, repr(l[:70]))
print("total lines",len(lines))
p2=os.path.join(root,"TXT","資持記","01_上一上.txt")
for i,l in enumerate(open(p2,encoding="utf-8").read().splitlines()[:16],1): print("JS",i,repr(l[:70]))
