# -*- coding: utf-8 -*-
import csv, json, os
W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"
rows = list(csv.reader(open(OUT, encoding="utf-8", newline=""), delimiter="\t", quotechar='"'))
print("rows:", len(rows), "fields:", set(len(r) for r in rows))
print("empty:", sum(1 for r in rows if not r[3].strip()),
      "tab:", sum(1 for r in rows if "\t" in r[3]),
      "nl:", sum(1 for r in rows if "\n" in r[3]))
keys = [(r[0], r[1], r[2]) for r in rows]
print("dup:", len(keys) - len(set(keys)))

recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
cur = {}
for r in recs:
    cur.setdefault((r["book"], r["chunk"], r["seg"]), set()).add(r["current"].rstrip("\n"))
print("segments with differing current:", [k for k, v in cur.items() if len(v) > 1])

iss = []
for r in rows:
    k = (r[0], r[1], r[2])
    c = list(cur[k])[0]
    n = r[3]
    for ch in ("\u300c", "\u300d", "\u3014", "\u3015"):
        pass
    if c.count("\u300c") - c.count("\u300d") != n.count("\u300c") - n.count("\u300d"):
        iss.append(("quote_delta", k, c.count("\u300c"), c.count("\u300d"), n.count("\u300c"), n.count("\u300d")))
    if c.count("\u3014") - c.count("\u3015") != n.count("\u3014") - n.count("\u3015"):
        iss.append(("brk_delta", k, c.count("\u3014"), c.count("\u3015"), n.count("\u3014"), n.count("\u3015")))
print("delta issues:", iss)

# absolute balance issues
abs_iss = []
for r in rows:
    n = r[3]
    if n.count("\u300c") != n.count("\u300d"):
        abs_iss.append(("q", r[1], r[2], n.count("\u300c"), n.count("\u300d")))
    if n.count("\u3014") != n.count("\u3015"):
        abs_iss.append(("b", r[1], r[2], n.count("\u3014"), n.count("\u3015")))
print("absolute issues:", abs_iss)
print("shortest:", sorted((len(r[3]) for r in rows))[:5])
