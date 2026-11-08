import csv, json, io
SRC = r"AI語譯/_work/review/report_dir.tsv"
rows = []
with open(SRC, "r", encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    hdr = next(r)
    for rec in r:
        if not rec or rec == [""]:
            continue
        if len(rec) != len(hdr):
            raise SystemExit("bad field count %d: %r" % (len(rec), rec[:3]))
        rows.append(dict(zip(hdr, rec)))
target = {"資持記", "05_拾毗尼義鈔"}
sel = [x for x in rows if x["book"] in target]
from collections import Counter
print("total", len(rows), "sel", len(sel))
print(Counter(x["book"] for x in sel))
print(Counter(x["level"] for x in sel))
print(Counter(x["cls"] for x in sel))
for i,x in enumerate(sel):
    print(i, x["gid"], x["book"], x["chunk"], "seg="+x["seg"], x["level"],
          "cur=%d"%len(x["current"]), "same" if x["current"]==x["tr"] else "diff")
json.dump(sel, open(r"AI語譯/_work/review/_g2d_rows.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
