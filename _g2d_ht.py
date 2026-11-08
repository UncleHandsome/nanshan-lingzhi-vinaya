import json
rows = json.load(open(r"AI語譯/_work/review/_g2d_rows.json", encoding="utf-8"))
out=[]
for i in range(48,85):
    x=rows[i]; c=x["current"]
    out.append("ROW %d gid=%s seg=%s len=%d" % (i,x["gid"],x["seg"],len(c)))
    out.append("  HEAD: "+c[:90])
    out.append("  TAIL: "+c[-90:])
open("_g2d_headtail.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
