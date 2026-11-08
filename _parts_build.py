# -*- coding: utf-8 -*-
import json, sys
sys.path.insert(0, ".")
from _parts_ops import OPS

rows = json.load(open("_parts_rows3.json", encoding="utf-8"))
by = {r["idx"]: r for r in rows}

# group by (chunk, seg), preserve first-appearance order
groups = []
gmap = {}
for r in rows:
    key = (r["chunk"], r["seg"])
    if key not in gmap:
        gmap[key] = []
        groups.append(key)
    gmap[key].append(r["idx"])

out_lines = []
stat = []
for key in groups:
    idxs = gmap[key]
    active = [i for i in idxs if i in OPS]
    if not active:
        continue
    base = by[active[0]]["current"]
    # ensure same base
    for i in active:
        assert by[i]["current"] == base, (i, key)
    new = base
    applied = []
    for i in active:
        for old, rep, cnt in OPS[i]:
            if old == "__APPEND__":
                new = new + rep
                applied.append(i)
                continue
            if old == "__PREPEND__":
                new = rep + new
                applied.append(i)
                continue
            c = new.count(old)
            assert c == cnt, (i, key, old, c, cnt)
            new = new.replace(old, rep)
            applied.append(i)
    assert new != base
    assert "\n" not in new and "\r" not in new and "\t" not in new, key
    r0 = by[active[0]]
    out_lines.append("%s\t%s\t%s\t%s" % ("資持記", r0["chunk"], r0["seg"], new))
    stat.append((key, active, len(new), len(base)))

with open("AI語譯/_work/review/fix_parts_g1.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out_lines) + "\n")

print("lines:", len(out_lines))
print("max len:", max(s[2] for s in stat))
print("min len:", min(s[2] for s in stat))
