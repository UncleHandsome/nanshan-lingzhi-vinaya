# -*- coding: utf-8 -*-
"""Append 卷中之四 rows to batch_qwen/r7k_done.tsv without touching existing rows."""
import os
P = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k_done.tsv"
rows = [
    (257, 0, 4, 0), (258, 0, 6, 0), (259, 1, 3, 0), (260, 3, 10, 1),
    (261, 2, 1, 0), (262, 4, 2, 0), (263, 4, 0, 0), (264, 3, 1, 0),
    (265, 0, 2, 0), (266, 3, 2, 0), (267, 2, 0, 0), (268, 2, 4, 0),
    (269, 2, 5, 0), (270, 2, 1, 0), (271, 2, 1, 0), (272, 2, 1, 0),
    (273, 3, 0, 0), (274, 2, 0, 0), (275, 0, 2, 0), (276, 4, 4, 0),
    (277, 3, 3, 0), (278, 4, 2, 0), (279, 3, 2, 0), (280, 3, 1, 0),
    (281, 0, 0, 0), (282, 4, 0, 0), (283, 3, 6, 0), (284, 1, 0, 0),
    (285, 3, 0, 0), (286, 2, 1, 0), (287, 2, 0, 0), (288, 1, 0, 0),
    (289, 2, 2, 0), (290, 4, 0, 0), (291, 4, 0, 0), (292, 5, 0, 0),
]
raw = open(P, "rb").read()
nl = b"\r\n" if b"\r\n" in raw else b"\n"
txt = raw.decode("utf-8-sig")
have = set()
for ln in txt.splitlines():
    f = ln.split("\t")[0].strip()
    if f.isdigit():
        have.add(int(f))
add = [r for r in rows if r[0] not in have]
assert len(add) == len(rows), "some rows already present: %s" % ([r[0] for r in rows if r[0] in have],)
body = txt if txt.endswith("\n") else txt + nl.decode()
body += "".join("%d\t卷中之四\t%d\t%d\t%d%s" % (r[0], r[1], r[2], r[3], nl.decode()) for r in add)
open(P, "wb").write(body.encode("utf-8"))
print("appended", len(add), "rows; newline", repr(nl))
