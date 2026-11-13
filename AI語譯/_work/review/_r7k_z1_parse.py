# -*- coding: utf-8 -*-
"""Parse 校閱 files for 卷中之一 and compare with current out chunks."""
import os, re, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
NUMS = []
with open(os.path.join(ROOT, r"AI語譯\_work\review\卷派工\01_行事鈔_卷中之一.tsv"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            NUMS.append(line.split("\t")[0])

def read_text(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

seg_re = re.compile(r"^【(\d+)-(\d+)】(\S+?)#(\d+)\s*$")
out = []
for n in NUMS:
    p = os.path.join(ROOT, "校閱_7K", f"校閱_{n}.txt")
    txt = read_text(p)
    lines = txt.splitlines()
    segs = []
    cur = None
    for ln in lines:
        m = seg_re.match(ln)
        if m:
            if cur: segs.append(cur)
            cur = {"file": n, "seg": m.group(2), "chunkpath": m.group(3), "chunk": m.group(3).split("/")[-1], "idx": int(m.group(4)), "src": "", "tr": ""}
            continue
        if cur is None: continue
        if ln.startswith("【原文】"):
            cur["src"] = ln[4:].strip()
            cur["mode"] = "src"
        elif ln.startswith("【譯文】"):
            cur["tr"] = ln[4:].strip()
            cur["mode"] = "tr"
        elif ln.strip() == "":
            continue
        elif cur.get("mode") == "tr":
            cur["tr"] += ln.strip()
        elif cur.get("mode") == "src":
            cur["src"] += ln.strip()
    if cur: segs.append(cur)
    # load chunk non-empty lines
    chunks = {}
    for s in segs:
        cp = s["chunk"]
        if cp not in chunks:
            data = read_text(os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", cp + ".txt"))
            ne = [x for x in data.splitlines() if x.strip()]
            chunks[cp] = ne
        ne = chunks[cp]
        s["cur"] = ne[s["idx"] - 1] if s["idx"] - 1 < len(ne) else "<OUT_OF_RANGE>"
        s["same"] = (s["cur"].strip() == s["tr"].strip())
    out.extend(segs)

print("files", len(NUMS), "segments", len(out))
for s in out:
    print(s["file"], s["seg"], s["chunk"], s["idx"], "SAME" if s["same"] else "DIFF", len(s["tr"]), len(s["cur"]))
with open(os.path.join(ROOT, r"AI語譯\_work\review\_r7k_z1_segs.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
