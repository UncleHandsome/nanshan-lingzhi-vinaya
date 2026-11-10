# -*- coding: utf-8 -*-
import io, json
p = r"AI語譯/_work/review/fix_re9_g2.tsv"
raw = open(p, "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "bytes:", len(raw), "CR:", raw.count(b"\r"))
text = raw.decode("utf-8")
lines = text.split("\n")
if lines and lines[-1] == "":
    lines = lines[:-1]
print("lines:", len(lines))
seen = set()
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
valid = {(d["book"], d["chunk"], d["seg"]) for d in rows}
ok = True
for i, l in enumerate(lines, 1):
    f = l.split("\t")
    if len(f) != 4:
        print("BAD", i, len(f)); ok = False; continue
    b, c, s, n = f
    if (b, c, s) not in valid:
        print("NOTARGET", i, b, c, s); ok = False
    if (b, c, s) in seen:
        print("DUP", b, c, s); ok = False
    seen.add((b, c, s))
    if not n.strip():
        print("EMPTY", i); ok = False
    if "\t" in n or "\n" in n or "\r" in n:
        print("CTRL", i); ok = False
    if n != n.strip():
        print("WS", i, repr(n[:10]), repr(n[-10:])); ok = False
print("ok:", ok, "unique:", len(seen))
