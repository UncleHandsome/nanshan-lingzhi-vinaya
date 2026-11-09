# -*- coding: utf-8 -*-
import json, re

data = json.load(open("AI語譯/_work/review/tmp_re8/groups.json", encoding="utf-8"))
rows = []
for line in open("AI語譯/_work/review/fix_re8_g3.tsv", encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    b, c, s, new = line.split("\t")
    rows.append((b, c, s, new))

print("rows:", len(rows))
bad = []
for b, c, s, new in rows:
    if new.count("「") != new.count("」"):
        bad.append(("QUOTE", b, c, s, new.count("「"), new.count("」")))
    if new.count("（") != new.count("）"):
        bad.append(("PAREN", b, c, s, new.count("（"), new.count("）")))
    for pat in ["，，", "。。", "  ", "、、", "；；"]:
        if pat in new:
            bad.append(("DUP", b, c, s, pat))
print("balance/dup issues:", len(bad))
for x in bad:
    print("  ", x)

# targeted windows
out = []
for b, c, s, new in rows:
    out.append(f"===== {b} | {c} | seg {s} | len={len(new)}")
    out.append(new)
open("AI語譯/_work/review/tmp_re8/final_all.txt", "w", encoding="utf-8").write("\n".join(out))
print("wrote final_all")
