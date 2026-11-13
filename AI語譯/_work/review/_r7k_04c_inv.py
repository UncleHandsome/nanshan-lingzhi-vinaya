import re, io, os, json
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
packets = [str(n) for n in range(2178, 2201)]
out = {}
for c in ("06a_卷下之下", "06b_卷下之下"):
    t = io.open(os.path.join(base, "AI語譯/out/04_比丘尼鈔", c + ".txt"), encoding="utf-8").read()
    out[c] = t
rows = []
missing = []
for p in packets:
    t = io.open(os.path.join(base, "校閱_7K", "校閱_%s.txt" % p), encoding="utf-8").read()
    segs = re.findall(r"^【(\d{4})-(\d{4})】(04_比丘尼鈔/\S+)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【|\n*$)", t, re.M | re.S)
    for g in segs:
        pid, sid, loc, sn, src, tr = g
        chunk = loc.split("/")[1].split("#")[0]
        ok = tr.strip() in out[chunk]
        if not ok:
            missing.append((p, sid, chunk, sn, tr[:40]))
        rows.append(dict(packet=p, sid=sid, chunk=chunk, seg=int(sn), src=src.strip(), tr=tr.strip(), ok=ok))
    # segments not captured
    tags = re.findall(r"^【(\d{4})-(\d{4})】", t, re.M)
    if len(tags) != len(segs):
        print("PARSE MISMATCH", p, len(tags), len(segs))
print("segments:", len(rows), "missing translations:", len(missing))
for m in missing[:10]:
    print("MISS", m)
from collections import defaultdict
d = defaultdict(list)
for r in rows:
    d[r["chunk"]].append(r["seg"])
for c, s in d.items():
    print(c, min(s), max(s), len(s), "unique", len(set(s)))
json.dump(rows, io.open(os.path.join(base, "AI語譯/_work/review/_r7k_04c_segs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
