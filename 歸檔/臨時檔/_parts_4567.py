import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
out=[]
for i in (4,5,67):
    r=by[i]
    out.append(f"### idx={i} {r['gid']} {r['chunk']} seg={r['seg']}")
    out.append("P: "+r["problem"]); out.append("S: "+r["suggestion"])
    out.append("C: "+r["current"])
    out.append("count 突吉羅=%d, count 破戒還俗=%d, count 事鈔業疏=%d" % (r["current"].count("突吉羅"), r["current"].count("破戒還俗"), r["current"].count("《事鈔業疏》")))
    out.append("")
open("_parts_4567.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
