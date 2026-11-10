import json,re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
cur={}
for x in d: cur[(x["chunk"],x["seg"])]=x["CUR"]
pats=["的的","地地","了了","是是","在在","又又","即即","來來","有有","不不","，，","。。","；；","：：","，、","、，","，；"]
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t"); t=f[3]; o=cur[(f[1],f[2])]
    for p in pats:
        if p in t and p not in o:
            print(f"{f[1]} {f[2]} [{p}] ...{t[max(0,t.find(p)-15):t.find(p)+15]}...")
