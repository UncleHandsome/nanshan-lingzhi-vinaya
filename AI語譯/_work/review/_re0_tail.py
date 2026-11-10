import json, io, os
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
spec = json.load(io.open(os.path.join(OUT, "spec.json"), encoding="utf-8-sig"))
lines=[]
for gid in spec:
    e = next(x for x in ents if x["gid"]==gid)
    lines.append("### %s %s#%d len=%d" % (gid, e["chunk"], e["seg"], len(e["current"] or "")))
    lines.append("TAIL: ..." + (e["current"] or "")[-260:])
    lines.append("SUG: " + (e["suggestion"] or "")[:200])
    lines.append("")
io.open(os.path.join(OUT,"tails.txt"),"w",encoding="utf-8").write("\n".join(lines))
print("ok")
