# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(base, "AI語譯", "out")
def paras(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]
o = paras(os.path.join(out, "03_業疏", "05b_卷一之五.txt"))
buf = []
for i in range(14, 23):
    buf.append(f"--- out[{i+1}] ---\n{o[i]}")
with open(os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx", "_05b_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
