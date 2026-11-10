import json
rows = json.load(open("_parts_rows2.json",encoding="utf-8"))
tot=0
for r in rows:
    tot += len(r["problem"])+len(r["suggestion"])+len(r["current"])+len(r["orig"])
print("total chars:", tot)
print("avg:", tot//len(rows))
print("max current:", max(len(r["current"]) for r in rows))
