# -*- coding: utf-8 -*-
import json, re
rows = json.load(open("_parts_rows3.json", encoding="utf-8"))
by = {r["idx"]: r for r in rows}

# rows excluded from OPS that had DIFF flag or suspicious status
check = [0,1,2,3,14,15,17,18,25,27,35,40,45,59,63,64,65,68,70,110,112,113,123,124,125,127,133,134,166,187,189]

out = []
for idx in check:
    r = by[idx]
    out.append("### idx=%d %s %s seg=%s %s %s same=%s" % (idx, r["gid"], r["chunk"], r["seg"], r["level"], r["cls"], r["same"]))
    out.append("P: " + r["problem"])
    out.append("S: " + r["suggestion"])
    out.append("C: " + r["current"])
    out.append("")
open("_parts_check2.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(check))
