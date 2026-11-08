# -*- coding: utf-8 -*-
p = r"AI語譯/out/資持記/11d_中四上.txt"
t = open(p, encoding="utf-8").read()
with open(r"AI語譯/_work/review/_fixwork/segcheck.txt", "w", encoding="utf-8") as f:
    i = t.find("其一、約定說法四句")
    f.write(f"found at {i}\n")
    if i >= 0:
        f.write(repr(t[max(0,i-300):i+200]) + "\n\n")
    paras = t.split("\n\n")
    f.write(f"paras {len(paras)}\n")
    for n, pa in enumerate(paras, 1):
        f.write(f"{n}\tlen={len(pa)}\t{pa[:40]!r}\n")
