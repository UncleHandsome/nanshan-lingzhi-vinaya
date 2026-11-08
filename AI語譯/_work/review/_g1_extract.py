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

print("header:", hdr)
print("total rows:", len(rows))
target = {"02_戒疏", "01_行事鈔", "04_比丘尼鈔"}
sel = [x for x in rows if x["book"] in target]
print("selected:", len(sel))
from collections import Counter
print(Counter(x["book"] for x in sel))
print(Counter(x["level"] for x in sel))
print(Counter(x["cls"] for x in sel))
for i, x in enumerate(sel):
    print(i, x["gid"], x["book"], x["chunk"], "seg=" + x["seg"],
          "cur=%d" % len(x["current"]), "prob=%d" % len(x["problem"]),
          "sug=%d" % len(x["suggestion"]),
          "same" if x["current"] == x["tr"] else "diff")
with open(r"AI語譯/_work/review/_g1_rows.json", "w", encoding="utf-8") as f:
    json.dump(sel, f, ensure_ascii=False, indent=1)
