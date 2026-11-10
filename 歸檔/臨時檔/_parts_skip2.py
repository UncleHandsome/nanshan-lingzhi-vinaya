import json
rows=json.load(open("_parts_rows3.json",encoding="utf-8"))
out=[l.rstrip("\n") for l in open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8")]
keys=set((l.split("\t")[1],l.split("\t")[2]) for l in out)
missing=[(r["idx"],r["gid"],r["chunk"],r["seg"]) for r in rows if (r["chunk"],r["seg"]) not in keys]
print("rows",len(rows),"out",len(out),"skipped",len(missing))
open("_parts_skipped.txt","w",encoding="utf-8").write("\n".join(str(m) for m in missing))
