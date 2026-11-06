import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
d=json.load(open(os.path.join(base,"ys_punct_in.json"),encoding="utf-8"))
keys=list(d.keys())
ids="0.1 0.2 0.4 0.5 0.6 0.7 0.8 0.10 0.34 0.35 0.43 0.44 0.45 0.46 0.47".split()
lines=[]
for s in ids:
    b,p=map(int,s.split("."))
    lines.append(f"{b}.{p}\t{d[keys[b]][p]}")
open(os.path.join(base,"punct_work","p0e.txt"),"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("ok",len(lines))
