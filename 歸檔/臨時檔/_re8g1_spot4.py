import random
rows=[l.rstrip("\n").split("\t") for l in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8")]
random.seed(7)
pick=random.sample(rows,10)
out=[]
for f in pick:
    out.append(f"=== {f[1]} {f[2]}\n{f[3]}\n")
open(r"AI語譯\_work\review\_spot4.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
