import json
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
need=set([6, 7, 8, 9, 12, 20, 22, 23, 24, 26, 28, 29, 30, 32, 33, 34, 36, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 56, 57, 58, 62, 69, 81, 82, 85, 86, 87, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 110, 112, 113, 123, 126, 129, 130, 131, 132, 136, 139, 140, 143, 144, 145, 146, 147, 148, 152, 153, 155, 156, 157, 158, 159, 161, 162, 163, 164, 165, 170, 171, 172, 173, 174, 176, 177, 178, 179, 191, 199, 200, 201, 202, 203, 204, 205, 206, 207, 209, 211, 213, 217, 219])
out=[]
for r in rows:
    if r["idx"] in need: continue
    st=r.get("_st2") or []
    tag="SAME" if r["same"] else "DIFF"
    out.append(f"[{r['idx']}] {r['gid']} {r['chunk']} seg={r['seg']} {r['level']} {r['cls']} {tag}")
    out.append("  P: "+r["problem"])
    out.append("  S: "+r["suggestion"])
    for X,Y,cx,cy in st:
        out.append(f"  pair: X={X!r} cnt={cx} | Y={Y!r} cnt={cy}")
    out.append("")
open("_parts_auto.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out), sum(len(x) for x in out))
