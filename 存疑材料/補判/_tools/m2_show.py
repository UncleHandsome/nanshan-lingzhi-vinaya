# -*- coding: utf-8 -*-
import json, os, sys
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
want = sys.argv[1:]
for r in rows:
    if r["id"] in want:
        print("=" * 70)
        print(r["id"], r["book"], r["chunk"], r["seg"])
        print("--CUR--")
        print(r["cur"])
        print("--SUG--")
        print(r["sug"])
