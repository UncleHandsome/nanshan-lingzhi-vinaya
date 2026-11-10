import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
for x in d:
    if x["chunk"]=="09a_卷二之三" and x["seg"]=="26":
        print("CUR:",x["CUR"])
        print("S:",x["S"])
ls=[l for l in open(r"AI語譯\out\03_業疏\09a_卷二之三.txt",encoding="utf-8").read().split("\n") if l.strip()]
print("BOOK:",ls[25])
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    if f[1]=="09a_卷二之三" and f[2]=="26":
        print("NEW :",f[3])
