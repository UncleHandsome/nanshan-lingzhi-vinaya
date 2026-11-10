# -*- coding: utf-8 -*-
import json, sys
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
nl = [d for d in rows if "\n" in d["current"]]
print("count", len(nl))
for d in nl:
    print("=" * 100)
    print(d["_line"], d["book"], d["chunk"], d["seg"], d["level"], d["cls"], "len", len(d["current"]))
    print("PROBLEM:", d["problem"][:300])
    print("SUG:", d["suggestion"][:300])
    print("CURRENT-REPR:", repr(d["current"][:400]))
    print("...TAIL:", repr(d["current"][-250:]))
