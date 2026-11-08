# -*- coding: utf-8 -*-
import json
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
lookup = {r["gid"]: r for r in recs}
lines = [l.split("\t") for l in open(BASE + r"\fix_qc.tsv", encoding="utf-8").read().split("\n") if l]
outmap = {}
for b, c, s, n in lines:
    for r in recs:
        if r["book"] == b and r["chunk"] == c and r["seg"] == s:
            outmap[r["gid"]] = n
out = []
for gid, key in [("06-0007", "惡見"), ("08-0194", "約束"), ("03-0015", "僧殘"), ("05-0203", "僧祇律")]:
    cur = lookup[gid]["current"]; new = outmap[gid]
    for label, txt in (("CUR", cur), ("NEW", new)):
        i = txt.find(key)
        out.append("%s %s @%d: ...%s..." % (gid, label, i, txt[max(0, i - 60):i + 80]))
open(BASE + r"\_qc_view2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("ok")
