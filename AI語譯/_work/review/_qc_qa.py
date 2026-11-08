# -*- coding: utf-8 -*-
import json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
lookup = {r["gid"]: r for r in recs}

lines = open(BASE + r"\fix_qc.tsv", encoding="utf-8").read().split("\n")
rows = [l.split("\t") for l in lines if l]
print("out rows", len(rows))
bad = []
for r in rows:
    if len(r) != 4:
        bad.append(("fields", r[0]))
outmap = {(r[0], r[1], r[2]): r[3] for r in rows}
report = []
for d in recs:
    key = (d["book"], d["chunk"], d["seg"])
    if key not in outmap:
        continue
    cur = d["current"]
    new = outmap[key]
    diffs = []
    if new == cur:
        diffs.append("IDENTICAL")
    if "\n" in new or "\t" in new:
        diffs.append("HASNL")
    if new.startswith('"') or new.endswith('"'):
        diffs.append("QUOTE_EDGE")
    if new != new.strip():
        diffs.append("WS_EDGE")
    for pat in ["。。", "，，", "；；", "：：", "、、", "（）", "〔〕", "「」", "」」", "「「"]:
        if pat in new and pat not in cur:
            diffs.append("DUP" + pat)
    if len(new) < 20:
        diffs.append("SHORT")
    report.append("%-9s len %d->%d %s" % (d["gid"], len(cur), len(new), " ".join(diffs)))
open(BASE + r"\_qc_qa.txt", "w", encoding="utf-8").write("\n".join(report) + "\n")
print("bad", bad)
