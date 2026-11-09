import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
src=open(r"_re8g1_build.py",encoding="utf-8").read()
ns={}
exec(src.split("# group rows by segment")[0], ns)
MANUAL=ns["MANUAL"]; SKIP=ns["SKIP"]
outkeys=set()
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t"); outkeys.add((f[1],f[2]))
segs={}
for x in d: segs.setdefault((x["chunk"],x["seg"]),[]).append(x)
unchanged=[k for k in segs if k not in outkeys]
print("unchanged segments:",len(unchanged))
for k in sorted(unchanged):
    print(" ",k)
    for x in segs[k]:
        key=(x["gid"],x["seg"],x["cls"])
        st = "SKIP" if key in SKIP else ("MANUAL" if key in MANUAL else f"pairs={len(x['pairs'])}")
        print("    ",x["gid"],x["cls"],st)
# count skipped rows
skipped=0
for x in d:
    key=(x["gid"],x["seg"],x["cls"])
    if key in SKIP: skipped+=1
print("skip rows:",skipped, "rows total with S:",len(d))
