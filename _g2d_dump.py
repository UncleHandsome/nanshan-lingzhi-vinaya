import json, sys
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
a, b, path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
def flat(s):
    return s.replace("\r\n","⏎").replace("\n","⏎").replace("\t","⇥")
out=[]
for i in range(a, min(b,len(rows))):
    x=rows[i]
    out.append("#### ROW %d | gid=%s | %s | %s | seg=%s | %s | %s" % (i,x["gid"],x["book"],x["chunk"],x["seg"],x["level"],x["cls"]))
    out.append("[PROBLEM] "+flat(x["problem"]))
    out.append("[SUGGESTION] "+flat(x["suggestion"]))
    out.append("[ORIG] "+flat(x["orig"]))
    out.append("[CURRENT] "+flat(x["current"]))
    out.append("")
open(path,"w",encoding="utf-8").write("\n".join(out))
print("wrote", path, b-a)
