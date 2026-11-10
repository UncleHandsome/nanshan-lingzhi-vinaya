import json, io, os
p = r"AI語譯\_work\review\report_re8.tsv"
rows=[]
with open(p, encoding="utf-8") as f:
    lines = f.read().split("\n")
print("total lines", len(lines))
hdr = lines[0].split("\t")
print("hdr", hdr, len(hdr))
bad=0
for i,l in enumerate(lines[1:], start=2):
    if not l.strip():
        bad+=1; continue
    f_ = l.split("\t")
    if len(f_)!=10:
        bad+=1
        print("BAD", i, len(f_), l[:120])
        continue
    rows.append(f_)
print("rows", len(rows), "bad", bad)
from collections import Counter
c = Counter(r[1] for r in rows)
print(c)
g1 = [r for r in rows if r[1]=="03_業疏"]
print("g1", len(g1))
# unique segments
segs = Counter((r[2],r[3]) for r in g1)
print("unique segs", len(segs))
nosug = [r for r in g1 if not r[7].strip()]
print("no suggestion", len(nosug))
json.dump(g1, open(r"AI語譯\_work\review\_re8g1_rows.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
# levels
print(Counter(r[4] for r in g1))
print(Counter(r[5] for r in g1))
