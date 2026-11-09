import json, re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
cur={}
for x in d: cur[(x["chunk"],x["seg"])]=x["CUR"]
pat=re.compile(r"([\u4e00-\u9fff，、；：]{4,12}?)\1")
n=0
out=[]
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    t=f[3]
    for m in pat.finditer(t):
        old=cur[(f[1],f[2])]
        if m.group(0) in old: continue
        n+=1
        out.append(f"{f[1]} {f[2]}: ...{t[max(0,m.start()-15):m.end()+15]}...")
print("dup candidates:",n)
print("\n".join(out[:40]))
