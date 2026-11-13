import json,os
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
pc=json.load(open(os.path.join(root,"AI語譯","_work","para_counts.json"),encoding="utf-8"))
d=os.path.join(root,"TXT_分卷","01_行事鈔")
for fn in sorted(os.listdir(d)):
    p=os.path.join(d,fn)
    lines=open(p,encoding="utf-8").read().splitlines()
    n=sum(1 for l in lines if l.startswith("\u3000\u3000"))
    stem=os.path.splitext(fn)[0]
    key="01_行事鈔/"+stem
    print(f"{stem:22s} indent_paras={n:4d}  para_counts={pc.get(key)}")
