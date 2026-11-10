import json, io
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT+"/uniq2.json", encoding="utf-8"))
rows = json.load(io.open(OUT+"/rows.json", encoding="utf-8"))
want = ["024-0013","029-0001","040-0011","050-0086","056-0092","059-0122","060-0009","066-0008","071-0021","080-0073","053-0063"]
out=[]
for r in rows:
    hit = [e for e in ents if e["book"]==r["book"] and e["chunk"]==r["chunk"] and e["seg"]==r["seg"] and e["gid"] in want]
    if hit:
        out.append("### %s %s#%d" % (hit[0]["gid"], r["chunk"], r["seg"]))
        out.append("OLD: "+r["old"])
        out.append("NEW: "+r["new"])
        out.append("")
io.open(OUT+"/review2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok", len(out))
