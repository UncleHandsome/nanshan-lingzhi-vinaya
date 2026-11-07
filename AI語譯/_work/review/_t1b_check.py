# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
out = os.path.join(base, "out")
def paras(book, chunk):
    with open(os.path.join(out, book, chunk + ".txt"), "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]
buf = []
for seg in (74, 75, 76, 77):
    p = paras("02_戒疏", "10c_卷三上之一")[seg-1]
    buf.append(f"[{seg}] {p}")
buf.append("---171---")
for seg in (170, 171, 172):
    p = paras("02_戒疏", "14b_卷三下之二")[seg-1]
    buf.append(f"[{seg}] {p}")
with open(os.path.join(base, "_work", "review", "_t1b_ctx", "_check_live.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
