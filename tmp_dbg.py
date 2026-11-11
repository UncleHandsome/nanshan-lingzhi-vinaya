import json,io
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
cl=json.load(io.open(ROOT+r"\AI語譯\_work\review\_r2_02\_claims2.json",encoding="utf-8"))
for c in cl:
    if "550-0003" in c["ids"] or c["resp"]==550 and "0003" in c["text"][:60]:
        print(c["cid"],c["resp"],c["ids"],c["text"][:150].replace("\n"," "))
print("--- resp550 total:",sum(1 for c in cl if c["resp"]==550))
for c in cl:
    if c["resp"]==550: print(c["cid"],c["ids"],c["text"][:80])
