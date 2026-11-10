# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0, r"AI語譯/_work/review")
from _build3_g1 import load, ops_for, norm

rows = load()
groups = {}
for d in rows:
    groups.setdefault((d["book"], d["chunk"], d["seg"]), []).append(d)

flags = []
for key, grp in groups.items():
    cur = grp[0]["current"]
    for d in grp:
        kind, ops = ops_for(d)
        for a, b in ops:
            for aa in (a, norm(a)):
                i = cur.find(aa)
                if i == -1: continue
                prev = cur[max(0, i-14):i]
                # longest suffix of prev that is a prefix of b
                best = 0
                for L in range(min(len(prev), len(b)), 3, -1):
                    if prev[-L:] == b[:L]:
                        best = L; break
                if best >= 4:
                    flags.append((d["_line"], key[1], key[2], best, prev[-12:], b[:20]))
                cur = cur[:i] + b + cur[i+len(aa):]
                break

print("duplication flags:", len(flags))
for f in flags:
    print(f)

# also scan outputs for immediate repeats of >=6 chars
print()
print("immediate repeats in output text:")
for key, grp in groups.items():
    cur = grp[0]["current"]
    for d in grp:
        kind, ops = ops_for(d)
        for a, b in ops:
            for aa in (a, norm(a)):
                if aa in cur:
                    cur = cur.replace(aa, b, 1); break
    txt = cur.rstrip("\n").replace("\n", "")
    for m in re.finditer(r"(.{6,20})\1", txt):
        print("  ", key[1], key[2], repr(m.group(0))[:60])
