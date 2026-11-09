# -*- coding: utf-8 -*-
import csv, json, io, os, re

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "report_r8b.tsv")
books = {"03_業疏", "05_拾毗尼義鈔"}

rows = []
with io.open(src, "r", encoding="utf-8-sig", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for r in rd:
        if (r.get("book") or "").strip() in books:
            rows.append({k: (v if v is not None else "") for k, v in r.items()})

out = io.open(os.path.join(base, "_r8b_g1_read2.txt"), "w", encoding="utf-8")
for i, r in enumerate(rows):
    out.write("### %d | %s | %s | seg %s | %s | %s\n" % (i, r["book"], r["chunk"], r["seg"], r["level"], r["cls"]))
    out.write("P: %s\n" % r["problem"].replace("\n", " / "))
    out.write("S: %s\n" % r["suggestion"].replace("\n", " / "))
    out.write("C: %s\n\n" % r["current"].replace("\n", " /NL/ "))
out.close()

# heuristic: does suggestion-quoted left phrase exist in current?
def quotes(s):
    return re.findall(r'「([^」]*)」', s)

report = []
for i, r in enumerate(rows):
    qs = quotes(r["suggestion"])
    left = qs[0] if qs else ""
    present = (left and left in r["current"])
    report.append("%d\tleft_present=%s\t%s" % (i, present, left[:40]))
io.open(os.path.join(base, "_r8b_g1_quotecheck.txt"), "w", encoding="utf-8").write("\n".join(report))
print("rows", len(rows))
