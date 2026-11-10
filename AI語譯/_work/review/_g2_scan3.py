# -*- coding: utf-8 -*-
import json, re
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
pats = ["修正為", "改作", "刪", "補", "增", "並將", "；並", "，並"]
for d in rows:
    sug = d["suggestion"].strip()
    if not sug: continue
    if "改為" in sug:
        hits = [p for p in ("修正為", "改作", "刪", "補", "並將") if p in sug]
    else:
        hits = ["NO_改為"]
    if hits:
        print("L%d s%s | %s | %s" % (d["_line"], d["seg"], ",".join(hits), sug[:160]))
