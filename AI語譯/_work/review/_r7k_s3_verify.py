# -*- coding: utf-8 -*-
"""改後核對：非空行數、與備份差異行數。"""
import os, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "資持記")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "資持記")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

for name in ["04a_上三", "04b_上三", "04c_上三"]:
    cur = rd(os.path.join(OUT, name + ".txt"))
    bak = rd(os.path.join(BAK, name + "_v.txt"))
    ce = "\r\n" if "\r\n" in cur else "\n"
    be = "\r\n" if "\r\n" in bak else "\n"
    cl = cur.split(ce)
    bl = bak.split(be)
    cn = [l for l in cl if l.strip()]
    bn = [l for l in bl if l.strip()]
    diff = sum(1 for a, b in zip(cn, bn) if a != b) if len(cn) == len(bn) else -1
    print("%s  EOL=%s  非空行 改前%d 改後%d  異動段=%d  全行數 %d/%d" % (
        name, "CRLF" if ce == "\r\n" else "LF", len(bn), len(cn), diff, len(bl), len(cl)))
    # 檢查同段落數與空行結構
    if len(bl) != len(cl):
        print("  !! 行數不一致")
