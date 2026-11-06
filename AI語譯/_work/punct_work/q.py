import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
d=json.load(open(os.path.join(base,"punct_work","draft.json"),encoding="utf-8"))
ids=["1.13","1.19","1.21","1.85","1.96","1.106","2.25","2.65","2.68","2.99","2.100","3.9","3.87","3.106","3.108","3.109","3.134"]
out=[]
for s in ids:
    b,p=map(int,s.split("."))
    t=d["blocks"][b]["texts"][p]
    out.append("=== "+s+" len="+str(len(t)))
    out.append(t)
open(os.path.join(base,"punct_work","quotes.txt"),"w",encoding="utf-8").write("\n".join(out))
print("ok")
