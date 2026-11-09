# -*- coding: utf-8 -*-
import json, re, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
def parse(r):
    s = r["suggestion"]
    m = re.match(r"^將「(.+?)」改為「(.+?)」", s) or re.search(r"將「(.+?)」改為「(.+?)」", s)
    if m: return m.group(1), m.group(2), "A"
    m = re.match(r"^「(.+?)」改為「(.+?)」", s) or re.search(r"「(.+?)」改為「(.+?)」", s)
    if m: return m.group(1), m.group(2), "B"
    m = re.search(r"^(?:.*?)\s*(.+?)\s*->\s*(.+)$", s)
    if m and "->" in s: return m.group(1).strip(), m.group(2).strip(), "C"
    return None, None, "E"
sel = []
for i, r in enumerate(rows):
    o, n, k = parse(r)
    if k not in ("A","B","C"): continue
    if "或" in (n or "") or "（" in (n or "") or len(o or "") < 16 or i+1 in (109,132,59,62,67):
        sel.append((i+1, r, o, n))
out=[]
for i, r, o, n in sel:
    out.append("R%d [%s] %s/%s" % (i, r["cls"], r["chunk"], r["seg"]))
    out.append("  P: " + r["problem"])
    out.append("  OLD: " + (o or ""))
    out.append("  NEW: " + (n or ""))
io.open(r"AI語譯\_work\review\_re4g1\risky.txt","w",encoding="utf-8").write("\n".join(out))
print(len(sel), "rows", len("\n".join(out)))
