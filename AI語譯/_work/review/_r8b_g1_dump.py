# -*- coding: utf-8 -*-
import csv, json, sys, io, os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "report_r8b.tsv")
books = {"03_業疏", "05_拾毗尼義鈔"}

rows = []
with io.open(src, "r", encoding="utf-8-sig", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for r in rd:
        if (r.get("book") or "").strip() in books:
            rows.append({k: (v if v is not None else "") for k, v in r.items()})

with io.open(os.path.join(base, "_r8b_g1_rows.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=0)

out = io.open(os.path.join(base, "_r8b_g1_read.txt"), "w", encoding="utf-8")
for i, r in enumerate(rows):
    out.write("=== #%03d | %s | %s | seg %s | %s | %s\n" % (i, r["book"], r["chunk"], r["seg"], r["level"], r["cls"]))
    out.write("[PROBLEM] %s\n" % r["problem"].replace("\n", " / "))
    out.write("[SUGGEST] %s\n" % r["suggestion"].replace("\n", " / "))
    out.write("[ORIG] %s\n" % r["orig"].replace("\n", " / "))
    out.write("[CURRENT] %s\n" % r["current"].replace("\n", " \\n "))
    out.write("\n")
out.close()
print("rows:", len(rows))
print("no_suggestion:", sum(1 for r in rows if not r["suggestion"].strip()))
print("has_nl_in_current:", sum(1 for r in rows if "\n" in r["current"]))
print("has_tab:", sum(1 for r in rows if "\t" in r["current"]))
