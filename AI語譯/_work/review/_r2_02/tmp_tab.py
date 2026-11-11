# -*- coding: utf-8 -*-
import io, os, json, collections
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
rows=[]
for line in io.open(os.path.join(HERE,"_apply2_log.jsonl"),encoding="utf-8"):
    line=line.strip()
    if line: rows.append(json.loads(line))
# merge rows by (chunk,seg): note list
agg=collections.OrderedDict()
for o in rows:
    k=(o["chunk"],o["seg"])
    agg.setdefault(k,[]).append(o.get("note",""))
lines=["| chunk | 段 | 處 | 改法摘要 |","|---|---:|---:|---|"]
for (ch,seg),notes in agg.items():
    tok=ch.split("_")[0]
    ns="；".join(dict.fromkeys([n for n in notes if n]))
    lines.append("| %s | %d | %d | %s |"%(tok,seg,len(notes),ns))
io.open(os.path.join(HERE,"_table.txt"),"w",encoding="utf-8").write("\n".join(lines))
print(len(agg),len(rows))
