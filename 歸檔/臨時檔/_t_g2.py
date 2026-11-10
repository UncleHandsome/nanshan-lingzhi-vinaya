import csv, io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
p = r"AI語譯\_work\review\report_re8.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh, delimiter="\t")
    hdr = next(rd)
    for r in rd:
        rows.append(r)
print("HDR", hdr, len(hdr))
print("nrows", len(rows))
from collections import Counter
c = Counter(r[1] for r in rows if len(r)>1)
for k,v in c.most_common():
    print(repr(k), v)
