import json
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
def flat(s): return s.replace("\r\n","⏎").replace("\n","⏎").replace("\t","⇥")
out=[]
for i in range(48,85):
    x=rows[i]
    out.append("#### ROW %d | gid=%s | %s | seg=%s | %s | %s | curlen=%d" % (i,x["gid"],x["chunk"],x["seg"],x["level"],x["cls"],len(x["current"])))
    out.append("[PROBLEM] "+flat(x["problem"]))
    out.append("[SUGGESTION] "+flat(x["suggestion"]))
    out.append("[ORIG] "+flat(x["orig"]))
    out.append("")
open("_g2d_ps.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
