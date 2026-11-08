# -*- coding: utf-8 -*-
import json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
lookup = {r["gid"]: r for r in recs}
out = []
for gid in ["08-0235", "08-0260", "09-0141", "09-0146", "09-0151", "09-0203", "06-0027", "08-0166", "08-0260"]:
    d = lookup[gid]
    out.append("===== " + gid + " seg" + d["seg"])
    out.append("PROBLEM: " + d["problem"])
    out.append("SUGGEST: " + d["suggestion"])
    out.append("ORIG: " + d["orig"][:400])
    out.append("CURRENT: " + d["current"])
open(BASE + r"\_qc_manual2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("ok")
