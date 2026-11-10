# -*- coding: utf-8 -*-
"""Emit manual-review digest for entries whose suggestion is not a clean replace,
plus a clean-ops JSON for automatic ones."""
import re, io, json, os
from collections import Counter, defaultdict

OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))

Q = re.compile(r"「([^「」]*)」")

def classify(e):
    pairs = e["pairs"]
    kind = pairs[0][0]
    cur = e["current"] or ""
    if kind in ("將A改為B", "A改為B"):
        olds = [p[1] for p in pairs]
        counts = [cur.count(o) for o in olds]
        if all(c == 0 for c in counts):
            return "OLDMISS"
        return "CLEAN"
    if kind == "刪除":
        return "CLEAN" if (pairs[0][1] and pairs[0][1] in cur) else "OLDMISS"
    if kind == "改為X":
        return "NEWONLY"
    return "OTHER"

for e in ents:
    e["cls"] = classify(e)

clean = [e for e in ents if e["cls"] == "CLEAN"]
manual = [e for e in ents if e["cls"] != "CLEAN"]
print("clean:", len(clean), "manual:", len(manual))
print(Counter(e["cls"] for e in manual))

lines = []
for e in sorted(manual, key=lambda x: (x["book"], x["chunk"], x["seg"], x["gid"])):
    cur = e["current"] or ""
    lines.append("### %s %s/%s#%d %s %s [%s]" % (e["gid"], e["book"], e["chunk"], e["seg"], e["prio"], e["type"], e["cls"]))
    lines.append("CUR(%d): %s" % (len(cur), cur))
    # which 問題 quotes are in current, with positions
    hits = []
    for q in Q.findall(e["problem"] or ""):
        if q and q in cur:
            hits.append("%s@%d" % (q, cur.find(q)))
    lines.append("QinCUR: " + " || ".join(hits))
    lines.append("PROB: " + (e["problem"] or ""))
    lines.append("SUG: " + (e["suggestion"] or ""))
    lines.append("")

io.open(os.path.join(OUT, "manual.txt"), "w", encoding="utf-8").write("\n".join(lines))
io.open(os.path.join(OUT, "clean_ops.json"), "w", encoding="utf-8").write(
    json.dumps([{"gid": e["gid"], "book": e["book"], "chunk": e["chunk"], "seg": e["seg"],
                 "type": e["type"], "pairs": e["pairs"]} for e in clean], ensure_ascii=False, indent=1))
print("manual.txt lines:", len(lines), "chars:", sum(len(l) for l in lines))
