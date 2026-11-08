import json, re, sys

rows = json.load(open(r"AI語譯\_work\review\_re2g1_rows.json", encoding="utf-8"))
print("rows", len(rows))

def quotes(s):
    return re.findall(r"「(.*?)」", s, re.S)

cnt = {"pair": 0, "nomatch": 0, "noq": 0, "multi": 0}
for i, r in enumerate(rows):
    s = r["suggestion"] or ""
    q = quotes(s)
    if not q:
        cnt["noq"] += 1
    elif len(q) >= 2:
        cnt["pair"] += 1
    else:
        cnt["nomatch"] += 1
print(cnt)

# check which quoted strings actually appear in current
appear = 0
missing = []
for i, r in enumerate(rows):
    cur = r["current"]
    q = quotes(r["suggestion"] or "")
    if q and q[0] in cur:
        appear += 1
    else:
        missing.append(i + 1)
print("first quote appears in current:", appear)
print("missing first quote:", len(missing))
print(missing)

# duplicate (chunk,seg)
from collections import Counter
c = Counter((r["chunk"], r["seg"]) for r in rows)
dups = {k: v for k, v in c.items() if v > 1}
print("dup segs:", dups)
for i, r in enumerate(rows, 1):
    if (r["chunk"], r["seg"]) in dups:
        print(" dup", i, r["gid"], r["chunk"], r["seg"])
