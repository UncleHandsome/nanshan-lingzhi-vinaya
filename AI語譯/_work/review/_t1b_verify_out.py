# -*- coding: utf-8 -*-
import csv, os, difflib

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
rev = os.path.join(base, "_work", "review")
out = os.path.join(base, "out")

def paras(book, chunk):
    with open(os.path.join(out, book, chunk + ".txt"), "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

rows = []
with open(os.path.join(rev, "fix_t1b.tsv"), "r", encoding="utf-8", newline="") as f:
    for row in csv.reader(f, delimiter="\t", quotechar='"'):
        if not row:
            continue
        assert len(row) == 4, row
        rows.append(row)

buf = [f"rows={len(rows)}"]
for book, chunk, seg, new in rows:
    assert "\n" not in new and "\t" not in new
    live = paras(book, chunk)[int(seg) - 1]
    assert live != new, ("unchanged", book, chunk, seg)
    buf.append(f"### {book} {chunk} {seg} old={len(live)} new={len(new)}")
    sm = difflib.SequenceMatcher(None, live, new)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            buf.append(f"{tag}: OLD[{live[i1:i2]}] NEW[{new[j1:j2]}]")
with open(os.path.join(rev, "_t1b_verify_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("OK", len(rows))
