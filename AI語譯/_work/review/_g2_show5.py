# -*- coding: utf-8 -*-
import json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
for ln in (33, 34, 40, 61, 74, 82, 352, 361, 375, 458, 493, 500):
    for d in rows:
        if d["_line"] == ln:
            print("=" * 90)
            print("L%d %s %s s%s" % (ln, d["book"], d["chunk"], d["seg"]))
            print("P:", d["problem"])
            print("S:", d["suggestion"])
