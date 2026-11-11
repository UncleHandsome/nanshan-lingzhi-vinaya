# -*- coding: utf-8 -*-
"""Dump 校閱 material segments for resp_NNN, with out-file line index.

usage: python _r2z2_seg.py 884 [--full]
"""
import os, re, io, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
OUTD = os.path.join(ROOT, "AI語譯", "out", "資持記")

LAB = re.compile(r"^【(\d+)-(\d+)】\s*(\S+?)/(\S+?)#(\d+)\s*$")

def load_out(chunk):
    p = os.path.join(OUTD, chunk + ".txt")
    with io.open(p, encoding="utf-8") as f:
        txt = f.read()
    lines = txt.split("\n")
    segs = [l for l in lines if l.strip()]
    return lines, segs

def parse_mat(n):
    p = os.path.join(MAT, f"校閱_{n:03d}.txt")
    with io.open(p, encoding="utf-8") as f:
        lines = [l.rstrip("\r\n") for l in f]
    entries = []
    cur = None
    for line in lines:
        m = LAB.match(line.strip())
        if m:
            cur = {"gid": m.group(1), "n2": m.group(2), "book": m.group(3),
                   "chunk": m.group(4), "seg": int(m.group(5)),
                   "src": None, "tr": None}
            entries.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("【原文】"):
            cur["src"] = line[4:]
        elif line.startswith("【譯文】"):
            cur["tr"] = line[4:]
    return entries

def main():
    n = int(sys.argv[1])
    full = "--full" in sys.argv
    entries = parse_mat(n)
    cache = {}
    for e in entries:
        ch = e["chunk"]
        if ch not in cache:
            cache[ch] = load_out(ch)[1]
        segs = cache[ch]
        idx = None
        if e["tr"] is not None:
            for i, s in enumerate(segs):
                if s == e["tr"]:
                    idx = i + 1
                    break
        e["line"] = idx
        print("=" * 70)
        print(f"[{e['gid']}-{e['n2']}] {e['book']}/{ch}#{e['seg']}  -> out {ch} line {idx}")
        if full:
            print("--原文--", e["src"])
            print("--譯文--", e["tr"])
        else:
            print("  原:", (e["src"] or "")[:60])
            print("  譯:", (e["tr"] or "")[:60])

main()
