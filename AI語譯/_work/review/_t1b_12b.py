# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(base, "AI語譯", "out")
work = os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx")

def paras(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

buf = []
for ch in ["12b_卷三之一", "13a_卷三之二"]:
    o = paras(os.path.join(out, "03_業疏", ch + ".txt"))
    buf.append(f"### {ch} n={len(o)}")
    if ch == "12b_卷三之一":
        rng = range(max(0, len(o) - 8), len(o))
    else:
        rng = range(0, 6)
    for i in rng:
        buf.append(f"{ch}[{i+1}]: {o[i]}")
with open(os.path.join(work, "_12b_tail.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("ok")
