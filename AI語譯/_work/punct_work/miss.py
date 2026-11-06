import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
inp=json.load(open(os.path.join(base,"ys_punct_in.json"),encoding="utf-8"))
keys=list(inp.keys())
out=[]
for key in ["2.30","2.86","2.102","3.24","3.45"]:
    b,p=map(int,key.split("."))
    out.append("=== "+key)
    out.append(inp[keys[b]][p])
open(os.path.join(base,"punct_work","miss.txt"),"w",encoding="utf-8").write("\n".join(out))
