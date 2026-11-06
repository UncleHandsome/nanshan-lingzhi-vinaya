import json,os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
M=set("，。、；：？！「」（）")
out=json.load(open(os.path.join(base,"ys_punct_out.json"),encoding="utf-8"))
for b in out["blocks"]:
    ts=b["texts"]
    print(b["key"].encode("unicode_escape").decode(), len(ts), sum(len(t) for t in ts), sum(1 for t in ts for c in t if c in M))
