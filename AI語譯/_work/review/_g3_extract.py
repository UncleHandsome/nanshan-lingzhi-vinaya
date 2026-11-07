import json, sys
p = r"AI語譯\_work\review\report_all.tsv"
books = {"資持記","01_行事鈔","04_比丘尼鈔","05_拾毗尼義鈔"}
rows=[]
bad=[]
with open(p, encoding="utf-8") as f:
    lines = f.read().split("\n")
hdr = lines[0].split("\t")
print("hdr:", hdr, len(hdr))
for ln, line in enumerate(lines[1:], start=2):
    if not line.strip():
        continue
    c = line.split("\t")
    if len(c) != len(hdr):
        bad.append((ln, len(c)))
        continue
    d = dict(zip(hdr, c))
    if d["book"] in books:
        rows.append(d)
print("target rows:", len(rows), "bad lines:", bad[:10], "nbad", len(bad))
with open(r"AI語譯\_work\review\_g3_rows.json","w",encoding="utf-8") as f:
    json.dump(rows,f,ensure_ascii=False,indent=0)
# stats
import collections
c=collections.Counter(r["book"] for r in rows); print(c)
c2=collections.Counter(r["cls"] for r in rows); print(c2)
for i,r in enumerate(rows):
    print(i, r["book"], r["chunk"], r["seg"], r["level"], len(r["current"]), len(r["problem"]), len(r["suggestion"]))
