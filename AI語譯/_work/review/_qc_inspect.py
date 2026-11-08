import csv, io

p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\report_qc.tsv"
raw = open(p, encoding="utf-8", newline="").read()
rows = list(csv.reader(io.StringIO(raw), delimiter="\t", quotechar='"'))
print("nrows", len(rows))
for i, r in enumerate(rows):
    print(i, len(r), [c[:18] for c in r[:3]])
