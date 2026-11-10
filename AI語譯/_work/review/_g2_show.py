# -*- coding: utf-8 -*-
import json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
for ln in (354, 369, 433, 309, 310, 311, 312, 359, 416, 446, 185, 342, 343, 360):
    for d in rows:
        if d["_line"] == ln:
            print("=" * 100)
            print("L%d %s %s s%s %s %s" % (ln, d["book"], d["chunk"], d["seg"], d["level"], d["cls"]))
            print("PROBLEM:", d["problem"])
            print("SUG:", d["suggestion"])
            print("CURRENT:", d["current"])
