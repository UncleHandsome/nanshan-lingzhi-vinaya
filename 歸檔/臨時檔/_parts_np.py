import json
rows = json.load(open("_parts_rows2.json",encoding="utf-8"))
out=[]
for r in rows:
    if not r.get("_pairs"):
        tag = "SAME" if r["same"] else "DIFF"
        out.append(f"[{r['idx']}] {r['gid']} {r['chunk']} seg={r['seg']} {r['level']} {r['cls']} {tag}")
        out.append("  S: "+r["suggestion"].replace("\n"," "))
open("_parts_nopair_sug.txt","w",encoding="utf-8").write("\n".join(out))
print("lines",len(out))
from collections import Counter
print(Counter((("SAME" if r["same"] else "DIFF")) for r in rows if not r.get("_pairs")))
