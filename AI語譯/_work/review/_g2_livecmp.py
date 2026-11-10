# -*- coding: utf-8 -*-
import json, re, io, os
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
groups = {}
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), d)
cache = {}
def para(book, chunk, seg):
    k = (book, chunk)
    if k not in cache:
        p = os.path.join("AI語譯", "out", book, chunk + ".txt")
        t = io.open(p, encoding="utf-8").read()
        cache[k] = [x.strip() for x in re.split(r"\r?\n\r?\n", t) if x.strip()]
    return cache[k][int(seg) - 1]
same = 0
diff = []
for k, d in groups.items():
    try:
        live = para(*k)
    except Exception as e:
        diff.append((k, "ERR " + str(e)))
        continue
    cur = d["current"].strip()
    if live == cur:
        same += 1
    else:
        diff.append((k, (len(cur), len(live)), cur[:60], live[:60]))
print("same:", same, "diff:", len(diff))
for x in diff[:40]:
    print("=" * 80)
    print(x)
