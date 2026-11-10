# -*- coding: utf-8 -*-
import io
for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    b, c, s, new = l.split("\t")
    if (c, s) in (("05a_卷下之上", "6"), ("16c_下四", "49")):
        print(b, c, s)
        for i, ch in enumerate(new):
            if ch == "『":
                print("   ...%s..." % new[max(0, i-60):i+60])
