import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
out=[]
for i in (93,99):
    c=by[i]["current"]
    j=c.find("【")
    out.append(f"{i} :: {c[j:]}")
open("_parts_chk.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
