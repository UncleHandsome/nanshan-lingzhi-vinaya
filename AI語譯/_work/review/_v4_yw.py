# -*- coding: utf-8 -*-
"""Dump 原文/譯文 digest to UTF-8 files."""
import json, os, sys
D = os.path.dirname(__file__)
d = json.load(open(os.path.join(D, "_v4_data.json"), encoding="utf-8"))
sel = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] else None
outp = sys.argv[2] if len(sys.argv) > 2 else "_v4_yw.txt"
buf = []
for r in d:
    if sel and str(r["file"]) not in sel: continue
    buf.append("=" * 12 + " 檔 %d " % r["file"] + "=" * 12)
    for s in r["segs"]:
        buf.append("【%s】(%s#%d)" % (s["label"], s["chunk"], s["idx"]))
        buf.append("原:" + s["yuanwen"])
    buf.append("")
open(os.path.join(D, outp), "w", encoding="utf-8").write("\n".join(buf))
print(outp, len("\n".join(buf)))
