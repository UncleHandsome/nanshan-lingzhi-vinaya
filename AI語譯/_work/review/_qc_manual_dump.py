# -*- coding: utf-8 -*-
import json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
recs = json.load(open(BASE + r"\_qc_rows.json", encoding="utf-8"))
want = """04-0164 04-0175 04-0179 04-0183 04-0193 05-0004 05-0005 05-0010 05-0022 05-0024
05-0053 05-0059 05-0074 05-0077 05-0086 05-0089 05-0100 05-0117 06-0067 06-0068
07-0206 07-0258 08-0194 09-0053 09-0124 09-0154""".split()
out = []
for d in recs:
    if d["gid"] in want:
        out.append("===== " + d["gid"] + " | " + d["book"] + " " + d["chunk"] + " seg" + d["seg"])
        out.append("PROBLEM: " + d["problem"])
        out.append("SUGGEST: " + d["suggestion"])
        out.append("ORIG: " + d["orig"])
        out.append("CURRENT: " + d["current"])
open(BASE + r"\_qc_manual.txt", "w", encoding="utf-8").write("\n".join(out))
print("written")
