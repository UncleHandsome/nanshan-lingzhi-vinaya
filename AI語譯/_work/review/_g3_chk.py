# -*- coding: utf-8 -*-
import io, os
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
for name in ["fix_loc_g1.tsv", "fix_parts_g3.tsv", "report_parts.tsv"]:
    p = os.path.join(BASE, name)
    b = open(p, "rb").read()
    print(name, "bytes=%d" % len(b), "BOM=%s" % b[:3].hex(), "CRLF=%d" % b.count(b"\r\n"), "LF=%d" % b.count(b"\n"))
# structural check of output
p = os.path.join(BASE, "fix_parts_g3.tsv")
lines = io.open(p, encoding="utf-8").read().split("\n")
if lines and lines[-1] == "": lines = lines[:-1]
print("out rows:", len(lines))
bad = [l for l in lines if len(l.split("\t")) != 4]
print("bad rows:", len(bad))
keys = [tuple(l.split("\t")[:3]) for l in lines]
print("unique keys:", len(set(keys)))
# any suspicious chars
susp = set()
for l in lines:
    for ch in l:
        if ch in "\ufffd\u0000":
            susp.add(ch)
print("suspicious chars:", susp)
print("sample3:", lines[2][:60])
