import re, os
root = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def read(p):
    with open(p, encoding="utf-8") as f: return f.read()
# sizes
print("== 分卷 01_行事鈔 sizes ==")
d=os.path.join(root,"TXT_分卷","01_行事鈔")
tot=0
for fn in sorted(os.listdir(d)):
    n=len(read(os.path.join(d,fn))); print(f"{fn:24s}{n:8d}")
print("== 記 sizes/lines ==")
d2=os.path.join(root,"TXT","資持記")
for fn in sorted(os.listdir(d2)):
    t=read(os.path.join(d2,fn)); print(f"{fn:16s} chars={len(t):7d} lines={t.count(chr(10))+1:6d}")
