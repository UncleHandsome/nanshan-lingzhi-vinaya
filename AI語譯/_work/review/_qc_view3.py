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
for gid in ["03-0166", "03-0178", "09-0124"]:
    d = [r for r in recs if r["gid"] == gid][0]
    a, b = d["current"], outmap[gid]
    out.append("=====" + gid + " len %d -> %d" % (len(a), len(b)))
    out.append("CUR head " + repr(a[:40]))
    out.append("CUR tail " + repr(a[-40:]))
    out.append("NEW head " + repr(b[:40]))
    out.append("NEW tail " + repr(b[-40:]))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op in sm.get_opcodes():
        if op[0] != "equal":
            tag, i1, i2, j1, j2 = op
            out.append("  %s @%d-%d %r -> %r" % (tag, i1, i2, a[i1:i2][:60], b[j1:j2][:60]))
open(BASE + r"\_qc_view3.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("ok")
