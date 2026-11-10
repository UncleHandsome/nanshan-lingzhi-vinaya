keys={("06b_卷一之六","118"),("07a_卷二之一","48"),("07b_卷二之一","114"),("11a_卷二之五","102"),("15b_卷三之四","36"),("14a_卷三之三","100")}
found=set()
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    if (f[1],f[2]) in keys: found.add((f[1],f[2]))
print("in output:",sorted(found))
print("missing:",keys-found)
# counts
rows=sum(1 for _ in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"))
print("rows",rows)
