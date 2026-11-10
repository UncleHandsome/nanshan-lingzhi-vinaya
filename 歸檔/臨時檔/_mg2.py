import json, io
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT+"/uniq2.json", encoding="utf-8"))
rows = json.load(io.open(OUT+"/rows.json", encoding="utf-8"))
want = ["021-0029","062-0081"]
out=[]
for g in want:
    e = next(x for x in ents if x["gid"]==g)
    r = next((x for x in rows if (x["book"],x["chunk"],x["seg"])==(e["book"],e["chunk"],e["seg"])), None)
    out.append("### %s %s#%d" % (g, e["chunk"], e["seg"]))
    out.append("NEW: " + (r["new"] if r else "NO ROW"))
    out.append("")
io.open(OUT+"/merged2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
