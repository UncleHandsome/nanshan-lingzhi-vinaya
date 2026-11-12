import json, os
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
for r in rows:
    print("### " + r["id"])
    print(r["judge"])
    print()
