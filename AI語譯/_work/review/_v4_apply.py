# -*- coding: utf-8 -*-
"""Apply targeted edits to out chunks.
Edits defined in _v4_edits.py as EDITS = [dict(chunk=..., label=..., old=..., new=...), ...]
Backup to 歸檔/7K卷修正前/01_行事鈔/<chunk>_v.txt (created once, before first edit).
"""
import os, sys, json, shutil, importlib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔")
D = os.path.dirname(__file__)
sys.path.insert(0, D)
import _v4_edits, _v4_edits2, _v4_edits3, _v4_edits4, _v4_edits5, _v4_edits6, _v4_edits7, _v4_edits8, _v4_edits9, _v4_edits10, _v4_edits11, _v4_edits12, _v4_edits13
importlib.reload(_v4_edits)
EDITS = _v4_edits.EDITS + _v4_edits2.EDITS + _v4_edits3.EDITS + _v4_edits4.EDITS + _v4_edits5.EDITS + _v4_edits6.EDITS + _v4_edits7.EDITS + _v4_edits8.EDITS + _v4_edits9.EDITS + _v4_edits10.EDITS + _v4_edits11.EDITS + _v4_edits12.EDITS + _v4_edits13.EDITS

dry = "--write" not in sys.argv

# load 校閱 data for label->chunk/idx
data = json.load(open(os.path.join(D, "_v4_data.json"), encoding="utf-8"))
lab2seg = {}
for r in data:
    for s in r["segs"]:
        lab2seg[s["label"]] = s

by_chunk = {}
for e in EDITS:
    sg = lab2seg.get(e["label"])
    assert sg, e
    assert sg["chunk"] == e["chunk"], (e, sg["chunk"])
    by_chunk.setdefault(e["chunk"], []).append(e)

os.makedirs(BAK, exist_ok=True)
report = []
for chunk, es in by_chunk.items():
    p = os.path.join(OUT, chunk + ".txt")
    raw = open(p, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8")
    lines = text.split(nl.decode())
    ne = [i for i, l in enumerate(lines) if l.strip()]
    orig = list(lines)
    for e in es:
        idx = lab2seg[e["label"]]["idx"] - 1
        li = ne[idx]
        line = lines[li]
        c = line.count(e["old"])
        if c != 1:
            report.append("FAIL %s: count=%d" % (e["label"], c))
            continue
        lines[li] = line.replace(e["old"], e["new"])
        report.append("OK   %s (%s#%d)" % (e["label"], chunk, idx + 1))
    changed = [i for i in range(len(lines)) if lines[i] != orig[i]]
    report.append("-- %s changed lines: %s" % (chunk, changed))
    if not dry:
        b = os.path.join(BAK, chunk + "_v.txt")
        if not os.path.exists(b):
            shutil.copy2(p, b)
            report.append("-- backup %s" % b)
        open(p, "wb").write(nl.join([l.encode("utf-8") for l in lines]))
report.append("dry=%s" % dry)
open(os.path.join(D, "_v4_apply.log"), "w", encoding="utf-8").write("\n".join(report))
print("\n".join(report))
