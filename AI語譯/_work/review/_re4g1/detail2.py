# -*- coding: utf-8 -*-
import json, re, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
D = [3,4,5,6,8,9,10,11,12,82,83,84,110,111,144,156,157]
E = [28,33,34,36,37,38,47,51,73,74,75,76,85,86,102,103,112,113,114]
out = []
for i in D+E:
    r = rows[i-1]; cur = r["current"]
    out.append("="*100)
    out.append("R%d %s %s/%s %s | CLS=%s" % (i, r["gid"], r["chunk"], r["seg"], r["level"], r["cls"]))
    out.append("P: " + r["problem"])
    out.append("S: " + r["suggestion"])
    if len(cur) <= 900:
        out.append("CUR: " + cur)
    else:
        out.append("CUR(len=%d): %s" % (len(cur), cur))
    out.append("")
io.open(r"AI語譯\_work\review\_re4g1\de.txt","w",encoding="utf-8").write("\n".join(out))
print("written", len("\n".join(out)))
