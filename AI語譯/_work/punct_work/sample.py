import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
out=json.load(open(os.path.join(base,"ys_punct_out.json"),encoding="utf-8"))
ids=[(3,0),(3,1),(3,2),(2,40),(2,60)]
buf=[]
for b,p in ids:
    t=out["blocks"][b]["texts"][p]
    buf.append("=== %d.%d len=%d"%(b,p,len(t)))
    buf.append(t)
open(os.path.join(base,"punct_work","sample.txt"),"w",encoding="utf-8").write("\n".join(buf))
print("ok")
