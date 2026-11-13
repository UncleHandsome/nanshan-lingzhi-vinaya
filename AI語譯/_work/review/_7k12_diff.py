# -*- coding: utf-8 -*-
import io, os
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔")
o = io.open(os.path.join(os.path.dirname(__file__), "_tmp_diff.txt"), "w", encoding="utf-8")
for c in ["12a_卷下之四", "12b_卷下之四", "12c_卷下之四"]:
    a = io.open(os.path.join(BAK, c + "_v.txt"), encoding="utf-8").read().split("\n")
    b = io.open(os.path.join(OUT, c + ".txt"), encoding="utf-8").read().split("\n")
    assert len(a) == len(b), (c, len(a), len(b))
    o.write("==== %s lines=%d\n" % (c, len(a)))
    n = 0
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            n += 1
            if n <= 3:
                o.write("line %d\nB: %s\nP: %s\n" % (i, x[:160], y[:160]))
    o.write("changed lines=%d\n" % n)
o.close()
print("done")
