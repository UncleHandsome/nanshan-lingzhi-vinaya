# -*- coding: utf-8 -*-
import json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
for ln in (352, 337, 341, 346, 349, 355, 356, 358, 364, 365, 366, 367, 368):
    for d in rows:
        if d["_line"] == ln:
            print("=" * 100)
            print("L%d %s %s s%s %s %s" % (ln, d["book"], d["chunk"], d["seg"], d["level"], d["cls"]))
            print("PROBLEM:", d["problem"])
            print("SUG:", d["suggestion"])
            print("CURRENT:", d["current"])
