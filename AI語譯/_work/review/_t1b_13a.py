# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(base, "AI語譯", "out")
work = os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx")

def paras(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

def lines(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return [x.rstrip("\n").strip("　 ") for x in f if x.strip()]

o = paras(os.path.join(out, "03_業疏", "13a_卷三之二.txt"))
s = lines(os.path.join(base, "TXT_分卷", "03_業疏", "13a_卷三之二.txt"))
buf = [f"src_lines={len(s)} out_paras={len(o)}"]
for i in range(0, 8):
    buf.append(f"src[{i+1}]: {s[i]}")
for i in range(0, 5):
    buf.append(f"out[{i+1}]: {o[i]}")
for i in range(60, 70):
    if i < len(s): buf.append(f"src[{i+1}]: {s[i]}")
for i in range(59, 68):
    if i < len(o): buf.append(f"out[{i+1}]: {o[i]}")
with open(os.path.join(work, "_13a_head.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(buf) + "\n")
print("ok")
