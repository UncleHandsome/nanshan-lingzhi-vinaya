import csv, io, json

p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\report_qc.tsv"
raw = open(p, encoding="utf-8", newline="").read()
rows = list(csv.reader(io.StringIO(raw), delimiter="\t", quotechar='"'))
hdr = rows[0]
recs = []
for r in rows[1:]:
    d = dict(zip(hdr, r))
    recs.append(d)
json.dump(recs, open(r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_qc_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

out = []
for d in recs:
    out.append(d["gid"] + " | " + d["suggestion"])
open(r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_qc_sug.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(recs))
