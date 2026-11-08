import json, os, sys

rows = json.load(open(r"AI語譯\_work\review\_g2x\rows.json", encoding="utf-8"))
out = []
for i, d in enumerate(rows, 1):
    out.append("=" * 100)
    out.append(f"[{i}] gid={d['gid']} book={d['book']} chunk={d['chunk']} seg={d['seg']} level={d['level']} cls={d['cls']} conf={d['conf']}")
    out.append("PROBLEM: " + d["problem"])
    out.append("SUGGESTION: " + d["suggestion"])
    out.append("ORIG: " + d["orig"])
    out.append("TR: " + d["tr"])
    out.append("CURRENT (" + str(len(d["current"])) + " chars): " + d["current"])
    out.append("")
text = "\n".join(out)
open(r"AI語譯\_work\review\_g2x\dump.txt", "w", encoding="utf-8").write(text)
print("lines:", text.count("\n"))
print("chars:", len(text))

# gid list
gids = [d["gid"] for d in rows]
from collections import Counter
for k, v in Counter(gids).items():
    if v > 1:
        print("DUP gid:", k, v)
