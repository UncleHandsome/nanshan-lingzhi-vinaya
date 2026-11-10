import json, difflib
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
book={}
for ch in set(x["chunk"] for x in d):
    book[ch]=[l for l in open(rf"AI語譯\out\03_業疏\{ch}.txt",encoding="utf-8").read().split("\n") if l.strip()]
out={}
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t"); out[(f[1],f[2])]=f[3]
ks=[("06b_卷一之六","118"),("07a_卷二之一","48"),("07b_卷二之一","114"),("11a_卷二之五","102"),("14a_卷三之三","100"),("15b_卷三之四","36")]
lines=[]
for k in ks:
    x=[y for y in d if (y["chunk"],y["seg"])==k][0]
    bk=book[k[0]][int(k[1])-1]
    lines.append(f"=== {k} {x['gid']}")
    lines.append(f"S: {x['S']}")
    lines.append(f"CUR: {x['CUR']}")
    lines.append(f"BOOK: {bk}")
    lines.append(f"NEW: {out.get(k)}")
    lines.append("")
open(r"AI語譯\_work\review\_six.txt","w",encoding="utf-8").write("\n".join(lines))
print("ok")
