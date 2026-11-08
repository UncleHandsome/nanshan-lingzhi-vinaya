import json, difflib
rows = json.load(open("_parts_rows.json",encoding="utf-8"))
out=[]
for r in rows:
    if not r["same"]:
        a=r["tr"]; b=r["current"]
        sm=difflib.SequenceMatcher(None,a,b)
        ops=[]
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag!="equal":
                ops.append(f"{tag}: tr[{i1}:{i2}]={a[i1:i2]!r} -> cur[{j1}:{j2}]={b[j1:j2]!r}")
        out.append(f"### {r['idx']} {r['gid']} {r['chunk']} seg={r['seg']} {r['level']} {r['cls']}")
        out.append("PROB: "+r["problem"])
        out.append("SUG : "+r["suggestion"])
        for o in ops: out.append("  "+o)
        out.append("")
open("_parts_diff.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
