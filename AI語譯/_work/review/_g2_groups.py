# -*- coding: utf-8 -*-
import json
from collections import OrderedDict
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
groups = OrderedDict()
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)

manual_lines = [23,53,79,88,89,100,101,102,104,105,106,107,108,109,115,122,164,165,170,171,172,173,174,177,181,182,183,184,185,309,310,311,312,336,342,343,348,350,351,352,353,354,360,361,362,363,369,375,411,416,421,433,434,446,454,455,456,457,458,459,471,473,486,493,496,498,499,500,501,502,507,508]
for key, rs in groups.items():
    lines = [d["_line"] for d in rs]
    if any(l in manual_lines for l in lines):
        print(key, "->", lines)
