# -*- coding: utf-8 -*-
"""Compact triage view for manual entries."""
import re, io, json, os
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))
loc = json.load(io.open(os.path.join(OUT, "locate.json"), encoding="utf-8"))
locmap = {(r["gid"], r["seg"]): r for r in loc}
Q = re.compile(r"「([^「」]*)」")

def cls_of(e):
    pairs = e["pairs"]; kind = pairs[0][0]; cur = e["current"] or ""
    if kind in ("將A改為B", "A改為B"):
        return "CLEAN" if any((p[1] or "").strip() and (p[1] in cur) for p in pairs) else "OLDMISS"
    if kind == "刪除":
        return "CLEAN" if (pairs[0][1] and pairs[0][1] in cur) else "OLDMISS"
    if kind == "改為X":
        return "NEWONLY"
    return "OTHER"

buffers = {}
for e in sorted(ents, key=lambda x: (x["book"], x["chunk"], x["seg"], x["gid"])):
    c = cls_of(e)
    if c == "CLEAN":
        continue
    cur = e["current"] or ""
    # anchor snippet
    anchor = None
    for q in Q.findall(e["problem"] or ""):
        if len(q) >= 6 and q in cur:
            anchor = (cur.find(q), len(q)); break
    if anchor:
        i, ln = anchor
        snip = "…" + cur[max(0, i - 90):i + ln + 90] + "…"
    else:
        snip = cur[:110] + ("　…　" + cur[-110:] if len(cur) > 240 else "")
    # locate info
    lr = locmap.get((e["gid"], e["seg"]))
    li = ""
    if lr:
        parts = []
        for kind, s, where, ln in lr["info"][:5]:
            parts.append("%s(%s,%d)" % (where, kind, ln))
        li = " ".join(parts)
    block = []
    block.append("### %s %s#%d %s [%s]" % (e["gid"], e["chunk"], e["seg"], e["type"], c))
    block.append("LOC: " + li)
    block.append("CUR: " + snip)
    block.append("PROB: " + (e["problem"] or "")[:400])
    block.append("SUG: " + (e["suggestion"] or "")[:500])
    block.append("")
    buffers.setdefault(e["book"], []).extend(block)

for book, lines in buffers.items():
    fn = os.path.join(OUT, "triage_%s.txt" % ("A" if book.startswith("01") else "B"))
    io.open(fn, "w", encoding="utf-8").write("\n".join(lines))
    print(book, len(lines), sum(len(x) for x in lines))
