import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
gids={"472-0016","476-0001","476-0026","491-0007","491-0016","492-0014","492-0024","493-0010","496-0009","496-0011"}
cur={}
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t")
    cur[(f[1],f[2])]=f[3]
out=[]
for x in d:
    if x["gid"] in gids:
        k=(x["chunk"],x["seg"])
        t=cur.get(k)
        if not t: continue
        i=t.find("或：") 
        out.append(f"=== {x['gid']} {k[0]} {k[1]}\n{t}\n")
open(r"AI語譯\_work\review\_spot2.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out),[x['gid'] for x in d if x['gid'] in gids])
