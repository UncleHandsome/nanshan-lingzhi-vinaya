import os
root = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
p=os.path.join(root,"TXT_分卷","01_行事鈔","05a_卷中之一.txt")
with open(p,encoding="utf-8") as f: lines=f.read().splitlines()
for i,l in enumerate(lines[:25],1):
    print(i, repr(l[:50]))
print("...")
for i,l in enumerate(lines[40:50],41):
    print(i, repr(l[:50]))
