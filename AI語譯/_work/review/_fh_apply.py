# -*- coding: utf-8 -*-
"""套用否決複審修正（逐處驗證 find 恰出現一次）。"""
import os, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")

EDITS = {
    "04a_卷一下之二.txt": [
        ("600-0006", "男女身分相交", "男女二根交接（身交）"),
        ("600-0009", "因為偷蘭遮與突吉羅本屬於個別的罪聚，經由這兩層意義全都歸入第一篇",
         "偷蘭遮與突吉羅雖然本屬於個別的罪聚，但由於這兩層意義，全都歸入第一篇"),
    ],
    "04c_卷一下之二.txt": [
        ("620-0012", "就外在事實來說其義理是相同的，但著眼的側重點不同。", "事義相同，但用意有別。"),
        ("621-0008", "如果依照教導造作外境就稱為作持", "如果依教對境造作就稱為作持"),
        ("622-0001", "是指僧房建造的尺寸規格", "是指房舍建造的尺寸規格"),
        ("622-0001", "如果確實有僧房和財物", "如果確實有房舍和衣財"),
        ("622-0013", "前面制定有所作為當中的止", "前面『制作』（制門作持）當中的止"),
        ("623-0004", "只因為其中兼具了『止（停止不作）』的意義", "只因為其中兼具了『止持（離過不犯）』的意義"),
        ("623-0013", "境想作法", "境想句"),
        ("629-0010", "因為他們並沒有違犯根本大戒，所以稱為止持。", "因為他們並沒有違犯根本（本條戒的正罪），所以稱為止持。"),
        ("629-0010", "對於事相與罪名有所迷惑", "對於事相與罪相有所迷惑"),
        ("629-0010", "就根本（不犯根本戒）這一宗要來判定義理", "就「不犯根本」這一宗要來判定義理"),
        ("632-0006", "『作犯』的位階當中", "『作犯』的門位當中"),
    ],
}


def main():
    for fname, ops in EDITS.items():
        p = os.path.join(OUT, fname)
        with io.open(p, "r", encoding="utf-8", newline="") as f:
            raw = f.read()
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        done = []
        for no, find, new in ops:
            hits = [i for i, l in enumerate(lines) if find in l]
            if len(hits) != 1:
                raise SystemExit("FAIL %s %s count=%d %r" % (fname, no, len(hits), find))
            i = hits[0]
            if lines[i].count(find) != 1:
                raise SystemExit("FAIL-inline %s %s count=%d" % (fname, no, lines[i].count(find)))
            lines[i] = lines[i].replace(find, new)
            done.append((no, i + 1))
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("%s: %d 處，EOL=%s" % (fname, len(ops), "CRLF" if eol == "\r\n" else "LF"))
        for no, ln in done:
            print("  %s  line %d" % (no, ln))


main()
