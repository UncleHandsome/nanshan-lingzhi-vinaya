import csv

path = r"AI語譯/_work/review/fix_err_g2.tsv"
raw = open(path, "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf")
print("bytes:", len(raw))
text = raw.decode("utf-8")
lines = text.split("\n")
print("trailing newline:", text.endswith("\n"))
lines = [l for l in lines if l != ""]
print("lines:", len(lines))
bad = 0
keys = set()
for i, l in enumerate(lines, 1):
    p = l.split("\t")
    if len(p) != 4:
        print("BAD FIELD COUNT", i, len(p))
        bad += 1
        continue
    book, chunk, seg, new = p
    if book != "03_業疏":
        print("BAD BOOK", i, book)
        bad += 1
    if not seg.isdigit():
        print("BAD SEG", i, seg)
        bad += 1
    if not new.strip():
        print("EMPTY NEW", i)
        bad += 1
    if any(c in new for c in "\t\r\n"):
        print("BAD CHAR", i)
        bad += 1
    keys.add((book, chunk, seg))
print("bad:", bad, "unique keys:", len(keys))

# all 70 report rows accounted for?
rep = []
with open(r"AI語譯/_work/review/report_err.tsv", encoding="utf-8") as f:
    for d in csv.DictReader(f, delimiter="\t"):
        if d["book"] == "03_業疏":
            rep.append((d["book"], d["chunk"], d["seg"]))
print("report rows:", len(rep), "out:", len(keys), "missing:", [k for k in rep if k not in keys])
