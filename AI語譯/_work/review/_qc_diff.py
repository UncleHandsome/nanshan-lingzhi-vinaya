# -*- coding: utf-8 -*-
import json, difflib
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
lines = [l.split("\t") for l in open(BASE + r"\fix_qc.tsv", encoding="utf-8").read().split("\n") if l]
outmap = {}
for b, c, s, n in lines:
    for r in recs:
        if r["book"] == b and r["chunk"] == c and r["seg"] == s:
            outmap[r["gid"]] = n
out = []
for d in recs:
    if d["gid"] not in outmap:
        continue
    a, b = d["current"], outmap[d["gid"]]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    edits = [op for op in sm.get_opcodes() if op[0] != "equal"]
    tot = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in edits)
    desc = "; ".join("%s %r->%r" % (tag, a[i1:i2][:50], b[j1:j2][:50]) for tag, i1, i2, j1, j2 in edits[:4])
    out.append("%-9s edits=%d span=%d %s" % (d["gid"], len(edits), tot, desc))
open(BASE + r"\_qc_diff.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("done")
