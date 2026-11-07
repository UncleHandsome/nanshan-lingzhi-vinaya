# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(base, "AI語譯", "out")
work = os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx")
def paras(book, chunk):
    with open(os.path.join(out, book, chunk + ".txt"), "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]
o = paras("03_業疏", "13a_卷三之二")
buf = []
for i in range(6, 16):
    buf.append(f"[{i+1}] {o[i]}")
with open(os.path.join(work, "_13a_7_16.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("ok")
