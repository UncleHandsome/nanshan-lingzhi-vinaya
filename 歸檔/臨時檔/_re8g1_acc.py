import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
g=json.load(open(r"AI語譯\_work\review\_re8g1_rows.json",encoding="utf-8"))
outkeys=set()
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t"); outkeys.add((f[1],f[2]))
insegs=sum(1 for x in d if (x["chunk"],x["seg"]) in outkeys)
print("report rows with S:",len(d),"in output segs:",insegs,"skipped:",len(d)-insegs)
print("total report rows(03):",len(g))
print("output rows:",len(outkeys))
# duplicates by paragraph text?
t={}
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    t.setdefault(f[3],[]).append((f[1],f[2]))
dups=[v for v in t.values() if len(v)>1]
print("duplicate texts:",len(dups), dups[:5])
