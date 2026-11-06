import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
inp=json.load(open(os.path.join(base,"ys_punct_in.json"),encoding="utf-8"))
out=json.load(open(os.path.join(base,"ys_punct_out.json"),encoding="utf-8"))
M=set("，。、；：？！「」（）")
print("top keys:",list(out.keys()))
print("blocks:",len(out["blocks"]))
ok=True
for i,b in enumerate(out["blocks"]):
    k=list(inp.keys())[i]
    print(i, b["key"]==k, len(b["texts"]), len(inp[k]))
    if b["key"]!=k or len(b["texts"])!=len(inp[k]): ok=False
tot_in=sum(len(t) for v in inp.values() for t in v)
tot_out=sum(len(t) for b in out["blocks"] for t in b["texts"])
marks=sum(1 for b in out["blocks"] for t in b["texts"] for c in t if c in M)
print("chars in/out",tot_in,tot_out,"marks",marks,"structure_ok",ok)
