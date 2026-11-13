# -*- coding: utf-8 -*-
"""追加 02_戒疏 後12 的處理記錄列（保留既有內容，不重複）。"""
import io, os

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
P = os.path.join(ROOT, "待跑_審查擋掉7K", "處理記錄.tsv")
ROWS = [
    ("695", 5, 0, 0),
    ("698", 3, 0, 0),
    ("699", 5, 0, 0),
    ("700", 5, 0, 0),
    ("701", 5, 0, 0),
    ("804", 7, 0, 0),
    ("841", 5, 1, 1),
    ("1098", 2, 1, 1),
    ("1112", 2, 0, 0),
    ("1207", 3, 0, 0),
    ("1250", 3, 1, 0),
    ("1256", 6, 0, 0),
]

raw = io.open(P, encoding="utf-8-sig", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
lines = [l for l in raw.split(eol)]
have = set(l.split("\t")[0] for l in lines if l.strip())
add = ["%s\t%d\t%d\t%d" % r for r in ROWS if r[0] not in have]
if add:
    while lines and lines[-1] == "":
        lines.pop()
    lines.extend(add)
    io.open(P, "w", encoding="utf-8", newline="").write(eol.join(lines) + (eol if raw.endswith(eol) else ""))
print("added %d rows; eol=%r" % (len(add), eol))
print(io.open(P, encoding="utf-8", newline="").read())
