# -*- coding: utf-8 -*-
"""Map resp_NNN -> 校閱_NNN -> chunk/seg list, for range 884+."""
import os, re, io, json, glob

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
SRC = os.path.join(ROOT, "batch_qwen", "r2")

LAB = re.compile(r"^【(\d+)-(\d+)】\s*(\S+?)/(\S+?)#(\d+)\s*$")

nums = sorted(int(re.search(r"(\d+)", os.path.basename(p)).group(1))
              for p in glob.glob(os.path.join(SRC, "resp_*.txt")))
nums = [n for n in nums if n >= 884]

rows = []
for n in nums:
    mf = os.path.join(MAT, f"校閱_{n:03d}.txt")
    if not os.path.exists(mf):
        rows.append({"n": n, "err": "no material"})
        continue
    labs = []
    with io.open(mf, encoding="utf-8") as f:
        for line in f:
            m = LAB.match(line.strip())
            if m:
                labs.append((m.group(3), m.group(4), int(m.group(5))))
    chunks = []
    for b, c, s in labs:
        if c not in chunks:
            chunks.append(c)
    rows.append({"n": n, "book": labs[0][0] if labs else None,
                 "chunks": chunks, "segs": [(c, s) for b, c, s in labs],
                 "cnt": len(labs)})

for r in rows:
    if r.get("err"):
        print(r["n"], "ERR", r["err"]); continue
    print(f"{r['n']}  book={r['book']}  n={r['cnt']}  chunks={r['chunks']}  "
          f"segs={r['segs'][0][1]}-{r['segs'][-1][1]}")
json.dump(rows, io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2z2_map.json"),
                        "w", encoding="utf-8"), ensure_ascii=False, indent=1)
