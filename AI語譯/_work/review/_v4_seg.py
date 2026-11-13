# -*- coding: utf-8 -*-
"""Show full 原文/譯文/現行 for given labels. usage: python _v4_seg.py 258-0001 258-0002 out.txt"""
import json, os, sys
D = os.path.dirname(__file__)
d = json.load(open(os.path.join(D, "_v4_data.json"), encoding="utf-8"))
labels = sys.argv[1].split(",")
outp = sys.argv[2] if len(sys.argv) > 2 else "_v4_seg.txt"
idx = {}
for r in d:
    for s in r["segs"]:
        idx[s["label"]] = s
buf = []
for lab in labels:
    lab = lab.strip()
    s = idx.get(lab)
    if not s:
        buf.append("!! %s not found" % lab); continue
    buf.append("#### %s (%s#%d) same=%s" % (lab, s["chunk"], s["idx"], s["same"]))
    buf.append("【原文】" + s["yuanwen"])
    buf.append("【譯文】" + s["yiwen"])
    if not s["same"]:
        buf.append("【現行】" + (s["cur"] or ""))
    buf.append("")
open(os.path.join(D, outp), "w", encoding="utf-8").write("\n".join(buf))
print(outp, len("\n".join(buf)))
