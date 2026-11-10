want={("10a_卷二之四","23"),("10b_卷二之四","76"),("14b_卷三之三","57"),("21b_卷四之四","28"),("21b_卷四之四","29"),("21b_卷四之四","88"),("13a_卷三之二","65"),("16a_卷三之五","23"),("08b_卷二之二","16"),("10b_卷二之四","56"),("05b_卷一之五","11"),("13b_卷三之二","73")}
out=[]
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    if (f[1],f[2]) in want:
        out.append(f"=== {f[1]} {f[2]}\n{f[3]}\n")
open(r"AI語譯\_work\review\_spot1.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
