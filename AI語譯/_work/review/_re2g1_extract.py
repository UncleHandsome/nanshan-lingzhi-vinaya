import csv, json, sys

SRC = r"AI語譯\_work\review\report_re2.tsv"
OUT = r"AI語譯\_work\review\_re2g1_dump.txt"
JSONOUT = r"AI語譯\_work\review\_re2g1_rows.json"

rows = []
with open(SRC, encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f, delimiter="\t")
    print("HEADER:", rd.fieldnames, file=sys.stderr)
    for r in rd:
        if r["book"] == "資持記":
            rows.append(r)

print("count:", len(rows), file=sys.stderr)

with open(JSONOUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

with open(OUT, "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, 1):
        f.write(f"===== [{i}] gid={r['gid']} chunk={r['chunk']} seg={r['seg']} level={r['level']} cls={r['cls']} conf={r['conf']}\n")
        f.write(f"--PROBLEM: {r['problem']}\n")
        f.write(f"--SUGGESTION: {r['suggestion']}\n")
        f.write(f"--ORIG: {r['orig']}\n")
        f.write(f"--TR: {r['tr']}\n")
        f.write(f"--CURRENT: {r['current']}\n")
print("wrote", OUT, file=sys.stderr)
