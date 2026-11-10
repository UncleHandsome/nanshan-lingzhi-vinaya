import csv, json, io
p = r"AI語譯\_work\review\report_re8.tsv"
csv.field_size_limit(10**9)
rows=[]
with open(p, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t", quotechar='"')
    hdr = next(r)
    for rec in r:
        if not rec or all(x=="" for x in rec):
            continue
        if len(rec)!=10:
            print("BADREC", len(rec), [x[:40] for x in rec])
            continue
        rows.append(rec)
print("rows", len(rows))
from collections import Counter
print(Counter(x[1] for x in rows))
g1=[x for x in rows if x[1]=="03_業疏"]
print("g1", len(g1))
segs = {}
for x in g1:
    segs.setdefault((x[2],x[3]), []).append(x)
print("unique segs", len(segs))
print("no sug", sum(1 for x in g1 if not x[7].strip()))
print("current empty", sum(1 for x in g1 if not x[9].strip()))
print("current multiline", sum(1 for x in g1 if "\n" in x[9]))
json.dump(g1, open(r"AI語譯\_work\review\_re8g1_rows.json","w",encoding="utf-8"), ensure_ascii=False)
# dump per segment view
out=[]
for (ch,seg), rs in sorted(segs.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
    out.append(f"##### chunk={ch} seg={seg} rows={len(rs)}")
    for i,x in enumerate(rs):
        out.append(f"[{x[0]}] L={x[4]} {x[5]}")
        out.append(f"  P: {x[6]}")
        out.append(f"  S: {x[7]}")
        out.append(f"  ORIG: {x[8]}")
    out.append(f"  CURRENT: {rs[0][9]}")
    out.append("")
open(r"AI語譯\_work\review\_re8g1_view.txt","w",encoding="utf-8").write("\n".join(out))
print("view written")
