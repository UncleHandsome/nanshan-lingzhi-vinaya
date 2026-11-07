import csv, os, json, sys

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
rp = os.path.join(base, "report_t1_located.tsv")
ap = os.path.join(base, "applied_t1_located.tsv")

def read_tsv(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f, delimiter="\t", quotechar='"')
        rows = [row for row in r]
    return rows

rrows = read_tsv(rp)
arows = read_tsv(ap)
print("report header:", rrows[0], len(rrows))
print("applied header:", arows[0], len(arows))
print("report col counts:", [len(x) for x in rrows[1:]])

applied = set()
for row in arows[1:]:
    if len(row) >= 3:
        applied.add((row[0], row[1], row[2]))
print("applied keys:", sorted(applied))

outdir = os.path.join(base, "_t1b_current")
os.makedirs(outdir, exist_ok=True)

meta = []
for i, row in enumerate(rrows[1:], start=2):
    if not row or row[0].strip() == "":
        continue
    book, chunk, seg = row[0], row[1], row[2]
    d = dict(zip(rrows[0], row))
    key = (book, chunk, seg)
    if key in applied:
        continue
    cur = d.get("current", "")
    if not cur.strip():
        print("SKIP empty current", key)
        continue
    fn = f"{book}__{chunk}__{seg}.txt"
    with open(os.path.join(outdir, fn), "w", encoding="utf-8") as f:
        f.write(cur)
    meta.append({"book": book, "chunk": chunk, "seg": seg, "level": d.get("level"),
                 "cls": d.get("cls"), "problem": d.get("problem"), "suggestion": d.get("suggestion"),
                 "orig": d.get("orig"), "tr": d.get("tr"), "file": fn, "len": len(cur)})

with open(os.path.join(outdir, "_meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)

print("unapplied count:", len(meta))
for m in meta:
    print(m["book"], m["chunk"], m["seg"], m["level"], m["cls"], m["len"], m["file"])
