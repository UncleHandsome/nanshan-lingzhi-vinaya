import csv, sys, io
p = r"AI語譯/_work/review/report_parts.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as f:
    r = csv.DictReader(f, delimiter="\t")
    hdr = r.fieldnames
    print("HDR:", hdr, file=sys.stderr)
    for row in r:
        rows.append(row)
print("total rows:", len(rows))
from collections import Counter
c = Counter(x["book"] for x in rows)
print(c)
book="資持記"
sel=[x for x in rows if x["book"]==book]
print("sel:", len(sel))
print("level:", Counter(x["level"] for x in sel))
print("cls:", Counter(x["cls"] for x in sel))
print("tr==current:", sum(1 for x in sel if x["tr"]==x["current"]))
print("tr!=current:", sum(1 for x in sel if x["tr"]!=x["current"]))
print("chunks:", Counter(x["chunk"] for x in sel))
