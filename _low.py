import json, io, difflib
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT + "/rows.json", encoding="utf-8"))
out=[]
for r in rows:
    old,new=r["old"],r["new"]
    sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
    if sm.ratio() < 0.80:
        out.append("### %s %s#%d ratio=%.3f %d->%d" % (r["book"],r["chunk"],r["seg"],sm.ratio(),len(old),len(new)))
        out.append("OLD: "+old)
        out.append("NEW: "+new)
        out.append("")
io.open(OUT+"/lowratio.txt","w",encoding="utf-8").write("\n".join(out))
print("count", len(out)//4)
