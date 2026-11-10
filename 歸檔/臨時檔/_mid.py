import json, io, difflib
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT + "/rows.json", encoding="utf-8"))
out=[]
for r in rows:
    old,new=r["old"],r["new"]
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    if sm.ratio() < 0.93:
        ops=[(t,old[i1:i2],new[j1:j2]) for t,i1,i2,j1,j2 in sm.get_opcodes() if t!="equal"]
        out.append("### %s %s#%d r=%.2f %d->%d" % (r["book"],r["chunk"],r["seg"],sm.ratio(),len(old),len(new)))
        for t,a,b in ops[:3]:
            out.append("  -%s" % a[:150])
            out.append("  +%s" % b[:150])
out.append("")
io.open(OUT+"/mid.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
