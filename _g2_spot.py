import csv
REP = r"AI語譯/_work/review/_g2fix/_g2_spot.txt"
want = {"16-0114","16-0305","16-0780","17-0177","17-0300","18-0010","19-0480","19-0802","18-0042","16-0001","19-0014","17-0141","16-0937","19-0373"}
cur = {}
order = []
with open(r"AI語譯/_work/review/report_err.tsv", encoding="utf-8") as f:
    for d in csv.DictReader(f, delimiter="\t"):
        if d["book"] == "03_業疏":
            cur[d["gid"]] = d
            order.append(d)
seg2gid = {(d["chunk"], d["seg"]): d["gid"] for d in order}
out = []
with open(r"AI語譯/_work/review/fix_err_g2.tsv", encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        gid = seg2gid[(p[1], p[2])]
        if gid in want:
            out.append(f"### {gid} {p[1]} seg{p[2]}\n[OLD] {cur[gid]['current']}\n[NEW] {p[3]}\n")
with open(REP, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("ok", len(out))
