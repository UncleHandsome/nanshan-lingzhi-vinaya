# -*- coding: utf-8 -*-
import json, io, os

SRC = r"AI語譯/_work/review/report_r8.tsv"
rows = []
with io.open(SRC, encoding="utf-8") as f:
    header = f.readline().rstrip("\n").split("\t")
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        p = line.split("\t")
        if len(p) < 10:
            print("SHORT LINE len=%d: %s" % (len(p), p[:3]))
            continue
        d = dict(zip(header, p))
        if d["book"] == "03_業疏":
            rows.append(d)

print("rows", len(rows))
out = []
for i, d in enumerate(rows, 1):
    out.append({
        "i": i, "gid": d["gid"], "chunk": d["chunk"], "seg": d["seg"],
        "level": d["level"], "cls": d["cls"],
        "problem": d["problem"], "suggestion": d["suggestion"],
        "orig": d["orig"], "current": d["current"],
        "clen": len(d["current"]),
    })
with io.open("_r8_rows.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for r in out:
    print("%02d %s %s seg=%s len=%d | %s" % (r["i"], r["gid"], r["chunk"], r["seg"], r["clen"], r["suggestion"][:60]))
