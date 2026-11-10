import csv, io, os
p = r"AI語譯/_work/review/report_err.tsv"
rows = []
with open(p, encoding="utf-8") as f:
    r = csv.DictReader(f, delimiter="\t")
    for d in r:
        if d["book"] == "03_業疏":
            rows.append(d)
print(len(rows))
os.makedirs(r"AI語譯/_work/review/_g2fix", exist_ok=True)
# dump in groups of 5
for i in range(0, len(rows), 5):
    grp = rows[i:i+5]
    lines = []
    for j, d in enumerate(grp):
        n = i + j + 1
        lines.append(f"===== ROW {n} | gid={d['gid']} | chunk={d['chunk']} | seg={d['seg']} | level={d['level']} | cls={d['cls']}")
        lines.append(f"[PROBLEM] {d['problem']}")
        lines.append(f"[SUGGESTION] {d['suggestion']}")
        lines.append(f"[ORIG] {d['orig']}")
        lines.append(f"[TR] {d['tr']}")
        lines.append(f"[CURRENT] {d['current']}")
        lines.append("")
    out = os.path.join(r"AI語譯/_work/review/_g2fix", f"grp_{i//5:02d}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(out, len("\n".join(lines)))
