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
targets = [87,90,116,117,124,27,58,134]
for i in targets:
    r = rows[i-1]; o,n,k = parse(r); cur = r["current"]
    print("="*100)
    print("R%d %s %s/%s %s" % (i, r["gid"], r["chunk"], r["seg"], r["cls"]))
    print("P:", r["problem"])
    print("S:", r["suggestion"])
    o,n,k = parse(r)
    anchor = (o or "")[:12]
    j = cur.find(anchor)
    if j < 0:
        # try first 8 chars
        anchor = (o or "")[:8]; j = cur.find(anchor)
    if j < 0: j = 0
    a=max(0,j-350); b=min(len(cur), j+450)
    print("CUR[%d:%d]: ...%s..." % (a,b,cur[a:b]))
    print()
