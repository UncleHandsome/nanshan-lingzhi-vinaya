# -*- coding: utf-8 -*-
"""Verify edits: each old must occur exactly once in the target segment line.
Usage: python _7k12_check.py   (no write)
"""
import os, sys, json
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import _7k12_edits
import importlib
importlib.reload(_7k12_edits)
EDITS = _7k12_edits.EDITS

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
data = json.load(open(os.path.join(D, "_7k12_data.json"), encoding="utf-8"))
lab2seg = {}
for r in data:
    for s in r["segs"]:
        lab2seg[s["label"]] = s

cache = {}
def lines_of(chunk):
    if chunk not in cache:
        raw = open(os.path.join(OUT, chunk + ".txt"), "rb").read()
        nl = b"\r\n" if b"\r\n" in raw else b"\n"
        cache[chunk] = raw.decode("utf-8-sig").split(nl.decode())
    return cache[chunk]

ne = {}
def nonempty(chunk):
    if chunk not in ne:
        ne[chunk] = [i for i, l in enumerate(lines_of(chunk)) if l.strip()]
    return ne[chunk]

bad = 0
for e in EDITS:
    sg = lab2seg[e["label"]]
    assert sg["chunk"] == e["chunk"], (e["label"], sg["chunk"])
    li = nonempty(e["chunk"])[sg["idx"] - 1]
    line = lines_of(e["chunk"])[li]
    c = line.count(e["old"])
    if c != 1:
        bad += 1
        print("FAIL %s count=%d" % (e["label"], c))
        if c == 0:
            print("   line has:", line[:200])
    else:
        print("OK   %s" % e["label"])
print("edits=%d bad=%d" % (len(EDITS), bad))
