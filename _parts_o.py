import json
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
out=[]
for i in (43,44,45,46):
    r=by[i]
    out.append(f"=== [{i}] {r['gid']} seg={r['seg']} ===")
    out.append("ORIG : "+r["orig"])
    out.append("PROB : "+r["problem"])
    out.append("SUG  : "+r["suggestion"])
    out.append("CUR  : "+r["current"])
    out.append("")
open("_parts_o.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
