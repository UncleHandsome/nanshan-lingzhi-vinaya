import json, re
rows = json.load(open(r"AI語譯\_work\review\_g3_rows.json", encoding="utf-8"))
pats = [r"將「([^」]{2,80})」", r"把「([^」]{2,80})」", r"「([^」]{2,80})」應改", r"刪除「([^」]{2,80})」"]
for i, r in enumerate(rows):
    s = r["suggestion"]
    xs = []
    for p in pats:
        xs += re.findall(p, s)
    if not xs:
        continue
    hit = [x for x in xs if x in r["current"]]
    if not hit:
        print(i, r["book"], r["chunk"], r["seg"], "| targets:", xs[:3])
