keys={("06a_卷一之六","48"),("06a_卷一之六","58"),("06a_卷一之六","66"),("11b_卷二之五","28"),("11b_卷二之五","29"),("21b_卷四之四","102"),("05b_卷一之五","108")}
out=[]
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    if (f[1],f[2]) in keys:
        out.append(f"=== {f[1]} {f[2]}\n{f[3]}\n")
open(r"AI語譯\_work\review\_spot3.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
