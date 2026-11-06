import json, os, re
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
d = json.load(open(os.path.join(base,"ys_punct_in.json"), encoding="utf-8"))
marks = "，。、；：？！「」（）"
out = []
out.append("keys: " + " || ".join(d.keys()))
tot=0; need=0; nonly=0
for k,v in d.items():
    np = sum(1 for t in v if not any(c in marks for c in t))
    np2 = sum(1 for t in v if sum(1 for c in t if c in marks) <= 2)
    out.append(f"{k}: n={len(v)} chars={sum(len(t) for t in v)} nopunct={np} le2={np2}")
    tot += sum(len(t) for t in v); need += np
out.append(f"TOTAL chars={tot} paragraphs_without_any_mark={need}")
open(os.path.join(base,"punct_work","summary.txt"),"w",encoding="utf-8").write("\n".join(out))
# listings
for bi,(k,v) in enumerate(d.items()):
    lines=[]
    for i,t in enumerate(v):
        lines.append(f"{i}\t{t}")
    open(os.path.join(base,"punct_work",f"list_{bi}.txt"),"w",encoding="utf-8").write("\n".join(lines))
print("done")
