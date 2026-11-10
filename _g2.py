import json, io
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
e = next(x for x in ents if x["gid"]=="036-0001")
ps = [s for s in io.open(r"AI語譯/out/11_行事鈔/11b_卷下之三.txt" if False else r"AI語譯/out/01_行事鈔/11b_卷下之三.txt", encoding="utf-8").read().split("\n") if s.strip()]
out=[]
for i,p in enumerate(ps):
    for k in ("碎裂","麻米","生身","舍利"):
        j=p.find(k)
        if j>=0:
            out.append("seg=%d term=%s ...%s..." % (i+1,k,p[max(0,j-70):j+70]))
            break
io.open(OUT+"/grep2.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
