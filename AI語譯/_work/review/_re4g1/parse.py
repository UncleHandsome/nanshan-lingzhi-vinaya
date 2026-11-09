# -*- coding: utf-8 -*-
import json, re, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
def parse(r):
    s = r["suggestion"]; p = r["problem"]; cur = r["current"]
    m = re.match(r"^將「(.+?)」改為「(.+?)」", s) or re.search(r"將「(.+?)」改為「(.+?)」", s)
    if m: return m.group(1), m.group(2), "A"
    m = re.match(r"^「(.+?)」改為「(.+?)」", s) or re.search(r"「(.+?)」改為「(.+?)」", s)
    if m: return m.group(1), m.group(2), "B"
    m = re.search(r"^(?:.*?)\s*(.+?)\s*->\s*(.+)$", s)
    if m and "->" in s: return m.group(1).strip(), m.group(2).strip(), "C"
    m = re.match(r"^改為「(.+?)」", s) or re.search(r"改為「(.+?)」", s)
    if m: return None, m.group(1), "D"
    return None, None, "E"
cnt = {}
for i, r in enumerate(rows):
    o, n, k = parse(r)
    cnt[k] = cnt.get(k,0)+1
print(cnt)
for k in "ABCDE":
    print("=== kind", k, "===")
    for i, r in enumerate(rows):
        o, n, kk = parse(r)
        if kk != k: continue
        st = ""
        if o:
            if o in r["current"]: st = "IN"
            else: st = "GONE"
        print("R%d|%s|%s|%s|%s|%s|%s" % (i+1, r["gid"], r["chunk"], r["seg"], st, (o or "")[:90], (n or "")[:120]))
