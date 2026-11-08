import json
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
nl=[(i,r["gid"],r["current"].count("\n")) for i,r in enumerate(rows) if "\n" in r["current"]]
print("rows with newline:", len(nl))
for t in nl: print(t)
print("tab in current:", sum(1 for r in rows if "\t" in r["current"]))
