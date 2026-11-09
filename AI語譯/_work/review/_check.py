import json, re, csv

out = "AI語譯/_work/review/fix_re5_g1.tsv"
rows = [l.rstrip("\n").split("\t") for l in open(out, encoding="utf-8")]
print("lines", len(rows))

jb = json.load(open("AI語譯/_work/review/_jb.json", encoding="utf-8"))
base = {}
for r in jb:
    base.setdefault((r["chunk"], r["seg"]), r["current"])

issues = []
for book, chunk, seg, new in rows:
    key = (chunk, seg)
    old = base[key]
    for pat, tag in [("（或", "alt-paren"), ("。。", "dbl-ju"), ("，。", "comma-ju"),
                     ("，，", "dbl-comma"), ("、、", "dbl-dun"), ("「「", "dbl-open"),
                     ("」」", "dbl-close"), ("（）", "empty-paren"), ("  ", "dbl-space"),
                     ("（）", "empty")]:
        if pat in new:
            issues.append((seg, tag, pat))
    if new.count("「") != new.count("」"):
        issues.append((chunk, seg, "quote-imbalance", new.count("「"), new.count("」")))
    if new.count("『") != new.count("』"):
        issues.append((chunk, seg, "inner-quote-imbalance", new.count("『"), new.count("』")))
    if len(new) - len(old) > 40 or len(old) - len(new) > 40:
        issues.append((chunk, seg, "len-delta", len(old), len(new)))
    if new == old:
        issues.append((chunk, seg, "unchanged",))

for x in issues:
    print(x)
print("total issues", len(issues))

# lengths
print("len new total", sum(len(r[3]) for r in rows))
