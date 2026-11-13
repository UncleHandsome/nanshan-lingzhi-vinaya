# -*- coding: utf-8 -*-
"""Align 校閱_7K segments (2232..2252, 2813) to current out paragraphs.
Writes _r7k5_map.json: {no: {chunk, idx, src, tr, lines:[i..j] (1-based non-empty), cur:"..."}}
Also prints per-file summary: exact or fuzzy match.
"""
import os, re, io, json, difflib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
NUMS = [2232, 2233, 2234, 2236, 2237, 2238, 2239, 2240, 2241, 2242, 2243, 2244,
        2245, 2246, 2247, 2248, 2249, 2250, 2251, 2252, 2813]

seg_re = re.compile(r"^【(\d+)-(\d+)】(\S+?)#(\d+)\s*$")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse(n):
    txt = rd(os.path.join(X7, "校閱_%d.txt" % n))
    segs, cur = [], None
    for ln in txt.splitlines():
        m = seg_re.match(ln.strip())
        if m:
            if cur:
                segs.append(cur)
            cur = {"no": m.group(1) + "-" + m.group(2), "file": n,
                   "chunkpath": m.group(3), "chunk": m.group(3).split("/")[-1],
                   "idx": int(m.group(4)), "src": "", "tr": "", "mode": None}
            continue
        if cur is None:
            continue
        if ln.startswith("【原文】"):
            cur["src"] = ln[4:].strip(); cur["mode"] = "src"
        elif ln.startswith("【譯文】"):
            cur["tr"] = ln[4:].strip(); cur["mode"] = "tr"
        elif not ln.strip():
            continue
        elif cur["mode"] == "tr":
            cur["tr"] += ln.strip()
        elif cur["mode"] == "src":
            cur["src"] += ln.strip()
    if cur:
        segs.append(cur)
    return segs


chunk_lines = {}


def nonempty(chunkpath):
    if chunkpath not in chunk_lines:
        book, name = chunkpath.split("/", 1)
        raw = rd(os.path.join(OUT, book, name + ".txt"))
        ne = [x.strip() for x in raw.replace("\r\n", "\n").split("\n") if x.strip()]
        chunk_lines[chunkpath] = ne
    return chunk_lines[chunkpath]


alls = []
for n in NUMS:
    alls.extend(parse(n))

# group by chunkpath, sort by idx
by_chunk = {}
for s in alls:
    by_chunk.setdefault(s["chunkpath"], []).append(s)
for cp in by_chunk:
    by_chunk[cp].sort(key=lambda x: x["idx"])

result = {}
for cp, segs in by_chunk.items():
    ne = nonempty(cp)
    pos = 0
    for k, s in enumerate(segs):
        target = s["tr"]
        # find start: first line at/after pos whose prefix matches target prefix
        found = None
        for st in range(pos, len(ne)):
            for en in range(st, min(len(ne), st + 40)):
                cand = "".join(ne[st:en + 1])
                if cand == target:
                    found = (st, en, 1.0)
                    break
                if len(cand) > len(target) + 3:
                    break
            if found:
                break
        if not found:
            # fallback: best ratio over spans
            best = (0, 0, 0.0)
            for st in range(pos, len(ne)):
                for en in range(st, min(len(ne), st + 40)):
                    cand = "".join(ne[st:en + 1])
                    r = difflib.SequenceMatcher(None, cand, target).ratio()
                    if r > best[2]:
                        best = (st, en, r)
                    if len(cand) > len(target) + 60:
                        break
            found = best
        st, en, r = found
        cur = "".join(ne[st:en + 1])
        s["lines"] = [st + 1, en + 1]
        s["ratio"] = round(r, 4)
        s["cur"] = cur
        pos = en + 1
        result[s["no"]] = s

with io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k5_map.json"),
             "w", encoding="utf-8", newline="\n") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

for s in alls:
    r = result[s["no"]]
    flag = "SAME" if r["cur"] == s["tr"] else ("FUZZ %.4f" % r["ratio"])
    print("%s %s#%d lines=%s %s (%d/%d)" % (s["no"], s["chunk"], s["idx"],
          r["lines"], flag, len(r["cur"]), len(s["tr"])))
print("total", len(alls), "chunks", list(by_chunk))
