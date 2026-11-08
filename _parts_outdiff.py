import json, difflib, sys
sys.path.insert(0,".")
from _parts_ops import OPS
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
by={r["idx"]:r for r in rows}
# rebuild mapping (chunk,seg) -> new
new={}
for line in open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8"):
    parts=line.rstrip("\n").split("\t")
    if len(parts)!=4: continue
    new[(parts[1],parts[2])]=parts[3]
out=[]
for r in rows:
    key=(r["chunk"],r["seg"])
    if key not in new: continue
    n=new[key]; c=r["current"]
    if n==c: continue
    sm=difflib.SequenceMatcher(None,c,n)
    ops=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        if tag=="replace": ops.append(f"[{c[max(0,i1-8):i1]}]{c[i1:i2]}→{n[j1:j2]}")
        elif tag=="delete": ops.append(f"[{c[max(0,i1-8):i1]}]{c[i1:i2]}→∅")
        elif tag=="insert": ops.append(f"[{c[max(0,i1-8):i1]}]∅→{n[j1:j2]}")
    out.append(f"### {r['idx']} {r['gid']} {r['chunk']} seg={r['seg']} | " + " ‖ ".join(ops))
open("_parts_outdiff.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
