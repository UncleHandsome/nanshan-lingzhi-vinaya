import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
ex=json.load(open(os.path.join(base,"punct_work","v3_extract.json"),encoding="utf-8"))
out=[]
for k in ["0.0","0.3","0.9","0.13","1.0","1.5","2.0","3.0","3.60","3.120"]:
    out.append("=== "+k)
    out.append(ex.get(k,"(missing)"))
open(os.path.join(base,"punct_work","preview_v3.txt"),"w",encoding="utf-8").write("\n".join(out))
print("ok")
