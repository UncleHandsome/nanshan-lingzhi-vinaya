# -*- coding: utf-8 -*-
import io, os
BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review"
SRC = os.path.join(BASE, "report_parts.tsv")
OUT = os.path.join(BASE, "fix_parts_g3.tsv")
simp = "说显来后众义无发问题过还这时个们将会学习现实体对开关节师传传统认识语言证实际为与专业务处理应"
simp = "".join(sorted(set(simp)))
src = {}
for line in io.open(SRC, encoding="utf-8"):
    line = line.rstrip("\r\n")
    if not line: continue
    c = line.split("\t")
    if len(c) == 13 and c[1] in ("02_戒疏", "03_業疏"):
        src[(c[1], c[2], c[3])] = c[10]
hits_new, hits_old = [], []
for line in io.open(OUT, encoding="utf-8"):
    line = line.rstrip("\r\n")
    if not line: continue
    c = line.split("\t")
    old = src[(c[0], c[1], c[2])]
    new = c[3]
    for ch in simp:
        if ch in new and ch not in old:
            hits_new.append((c[0], c[2], ch, new[max(0,new.find(ch)-12):new.find(ch)+12]))
        if ch in old and ch not in new:
            hits_old.append((c[0], c[2], ch))
print("simplified chars introduced:", len(hits_new))
for h in hits_new[:20]: print(h)
print("simplified chars removed:", hits_old)
