import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
M=set("，。、；：？！「」（）")
inp=json.load(open(os.path.join(base,"ys_punct_in.json"),encoding="utf-8"))
out=json.load(open(os.path.join(base,"ys_punct_out.json"),encoding="utf-8"))
def st(s): return "".join(c for c in s if c not in M)
bad=0; empty=0; n=0
for i,b in enumerate(out["blocks"]):
    k=list(inp.keys())[i]
    assert b["key"]==k
    for j,(a,c) in enumerate(zip(inp[k],b["texts"])):
        n+=1
        if st(a)!=st(c): bad+=1
        if not c.strip(): empty+=1
print("paragraphs",n,"char_mismatch",bad,"empty",empty)
print("size",os.path.getsize(os.path.join(base,"ys_punct_out.json")))
