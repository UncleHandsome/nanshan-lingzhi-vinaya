import csv
rows=[]
with open(r"AI語譯/_work/review/report_err.tsv",encoding="utf-8") as f:
    for d in csv.DictReader(f,delimiter="\t"):
        if d["book"]=="03_業疏": rows.append(d)
for d in rows:
    if d["gid"] in ("17-0061","18-0014"):
        print("="*20, d["gid"], d["chunk"], d["seg"])
        print("[PROB]", d["problem"])
        print("[SUG]", d["suggestion"])
        print("[CUR]", d["current"])
        print()
