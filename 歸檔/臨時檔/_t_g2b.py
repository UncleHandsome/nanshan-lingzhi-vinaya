import csv, sys, json
sys.stdout.reconfigure(encoding="utf-8")
p = r"AI語譯\_work\review\report_re8.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh, delimiter="\t")
    hdr = next(rd)
    for r in rd:
        rows.append(r)
sel = [r for r in rows if r[1]=="04_比丘尼鈔"]
from collections import Counter, OrderedDict
chunks = OrderedDict()
for r in sel:
    chunks.setdefault(r[2], []).append(r)
print("chunks", len(chunks))
for k,v in chunks.items():
    print(repr(k), len(v), "segs", sorted(int(x[3]) for x in v))
print("levels", Counter(r[4] for r in sel))
print("cls", Counter(r[5] for r in sel))
json.dump(sel, open("_g2rows.json","w",encoding="utf-8"), ensure_ascii=False)
