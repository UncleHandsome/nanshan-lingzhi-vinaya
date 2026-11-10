import json, re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
cur={}
for x in d: cur[(x["chunk"],x["seg"])]=x["CUR"]
bads=["，。","。。","，，","；。","、、","（）","」」","「「","，）","（，","。，","；；",",",";;"]
rep={}
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    t=f[3]; k=(f[1],f[2])
    for b in bads:
        if b in t:
            rep.setdefault(b,[]).append((k,t[max(0,t.find(b)-12):t.find(b)+12]))
for b,v in rep.items():
    print("==",b,len(v))
    for x in v[:6]: print("   ",x)
