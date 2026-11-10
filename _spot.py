import json, io, sys, difflib
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT+"/rows.json", encoding="utf-8"))
ents = json.load(io.open(OUT+"/uniq2.json", encoding="utf-8"))
want = ["018-0024","019-0014","033-0004","051-0004","052-0061","062-0120","064-0081","066-0008","067-0026","071-0084","072-0062","078-0028","080-0073","086-0004","087-0032","069-0078"]
bykey = {(e["book"],e["chunk"],e["seg"]): e for e in ents}
out=[]
for r in rows:
    e = bykey[(r["book"],r["chunk"],r["seg"])]
    if e["gid"] in want:
        sm=difflib.SequenceMatcher(None,r["old"],r["new"],autojunk=False)
        out.append("### %s %s#%d" % (e["gid"], r["chunk"], r["seg"]))
        for t,i1,i2,j1,j2 in sm.get_opcodes():
            if t!="equal":
                out.append("  - %s" % r["old"][i1:i2])
                out.append("  + %s" % r["new"][j1:j2])
        out.append("")
io.open(OUT+"/spot.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
