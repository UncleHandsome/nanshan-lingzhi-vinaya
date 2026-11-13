# -*- coding: utf-8 -*-
"""Apply _7k12_edits.EDITS to out chunks, with backup."""
import os, sys, json, shutil, importlib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔")
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import _7k12_edits
importlib.reload(_7k12_edits)
EDITS = _7k12_edits.EDITS

dry = "--write" not in sys.argv

data = json.load(open(os.path.join(D, "_7k12_data.json"), encoding="utf-8"))
lab2seg = {s["label"]: s for r in data for s in r["segs"]}

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
open(os.path.join(D, "_7k12_apply.log"), "w", encoding="utf-8").write("\n".join(report))
print("\n".join(report))
