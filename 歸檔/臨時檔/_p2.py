import json, io, re
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT + "/rows.json", encoding="utf-8"))
bad=[]
for r in rows:
    old,new=r["old"],r["new"]
    for pat in ["。。","，，","，。","、。","：。","；。","？。","！。","。」。","」」，","，，","。。"]:
        if pat in new and pat not in old:
            bad.append((r["book"],r["chunk"],r["seg"],pat,new[max(0,new.find(pat)-30):new.find(pat)+10]))
out=["%s %s#%d %s ...%s..." % b for b in bad]
io.open(OUT+"/punct2.txt","w",encoding="utf-8").write("\n".join(out))
print(len(bad))
