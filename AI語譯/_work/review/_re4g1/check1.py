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
    m = re.match(r"^改為「(.+?)」", s) or re.search(r"改為「(.+?)」", s)
    if m: return None, m.group(1), "D"
    return None, None, "E"
def norm(t):
    return re.sub(r"[「」『』\"'“”‘’\s]", "", t)
print("### GONE rows check")
for i, r in enumerate(rows):
    o, n, k = parse(r)
    if not o or o in r["current"]: continue
    no = norm(o); nc = norm(r["current"])
    status = "FUZZY_FOUND" if no in nc else "NOT_FOUND"
    print("R%d %s %s/%s %s | old=%s | new=%s" % (i+1, r["gid"], r["chunk"], r["seg"], status, o[:80], (n or "")[:100]))
print()
print("### MULTI-OCCURRENCE rows")
for i, r in enumerate(rows):
    o, n, k = parse(r)
    if not o: continue
    c = r["current"].count(o)
    if c > 1:
        print("R%d count=%d old=%s" % (i+1, c, o[:90]))
print()
print("### SUSPICIOUS new (unbalanced quotes / truncated)")
for i, r in enumerate(rows):
    o, n, k = parse(r)
    if not n: continue
    if n.count("「") != n.count("」") or n.endswith("「") or re.search(r"「[^」]{0,6}$", n):
        print("R%d %s old=%s NEW=%s" % (i+1, r["gid"], (o or "")[:70], n[:120]))
