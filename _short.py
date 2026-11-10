import json, io
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT + "/rows.json", encoding="utf-8"))
# also need per-op info: reload ents and decisions to list short olds
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
out=[]
for e in sorted(ents, key=lambda x:(x["book"],x["chunk"],x["seg"])):
    for p in e["pairs"]:
        if p[0] in ("將A改為B","A改為B") and p[1] and len(p[1])<=14:
            cur=e["current"] or ""
            if p[1] in cur:
                out.append("%s seg=%d old=%r new=%r" % (e["gid"], e["seg"], p[1], p[2][:60]))
io.open(OUT+"/short_olds.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
