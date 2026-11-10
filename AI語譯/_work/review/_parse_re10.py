import csv, re, json, sys

path = r"AI語譯/_work/review/report_re10.tsv"
rows = []
with open(path, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for row in r:
        if not row:
            continue
        rows.append(dict(zip(header, row)))

print("cols:", header)
print("nrows:", len(rows))

pat = re.compile(r"「([^「」]*)」")
for row in rows:
    sug = row["suggestion"]
    toks = pat.findall(sug)
    print("=" * 20)
    print(row["gid"], row["book"], row["chunk"], row["seg"], "tokens:", len(toks))
    for i, t in enumerate(toks):
        print(f"  [{i}] {t}")
