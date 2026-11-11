# -*- coding: utf-8 -*-
"""Map 校閱_10K material files -> segments; list 資持記 ones."""
import os, re, io, json, glob
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
pat = re.compile(r"^【(\d{3})-(\d{4})】\s*([^/\s]+)/([^#\s]+)#(\d+)\s*$")
out = []
missing = []
for p in sorted(glob.glob(os.path.join(MAT, "校閱_*.txt"))):
    n = int(re.search(r"校閱_(\d+)\.txt$", p).group(1))
    txt = io.open(p, encoding="utf-8").read()
    body = txt.split("# 材料開始", 1)[-1]
    segs = []
    for line in body.split("\n"):
        m = pat.match(line.strip())
        if m:
            segs.append({"gid": m.group(1) + "-" + m.group(2), "book": m.group(3),
                         "chunk": m.group(4), "seg": int(m.group(5))})
    if not segs:
        missing.append(n)
    z = [s for s in segs if s["book"] == "資持記"]
    if z:
        out.append({"n": n, "zhichi": z, "nseg": len(segs),
                    "books": sorted(set(s["book"] for s in segs))})
print("files with 資持記:", len(out))
print("total 資持記 segs in material:", sum(len(o["zhichi"]) for o in out))
for o in out:
    print(o["n"], o["nseg"], o["books"], [(z["chunk"], z["seg"]) for z in o["zhichi"]][:6],
          "..." if len(o["zhichi"]) > 6 else "")
print("no-seg files:", len(missing), missing[:20])
json.dump(out, io.open(os.path.join(ROOT, "AI語譯/_work/review/_r2z_mat.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
