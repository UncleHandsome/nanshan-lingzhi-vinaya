# -*- coding: utf-8 -*-
"""Verify fix_re5_g2.tsv: every output line's diff vs report `current` must consist
only of the intended edits; check format and coverage."""
import csv, json, os, difflib

BASE = r"AI語譯\_work\review"
rows = json.load(open(os.path.join(BASE, "_g2r", "rows.json"), encoding="utf-8"))
cur = {}
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    cur.setdefault(k, d["current"])

out = []
with open(os.path.join(BASE, "fix_re5_g2.tsv"), encoding="utf-8", newline="") as f:
    for ln in f:
        ln = ln.rstrip("\n").rstrip("\r")
        if not ln:
            continue
        parts = ln.split("\t")
        assert len(parts) == 4, ("bad field count", len(parts), ln[:40])
        out.append(tuple(parts))

print("lines:", len(out))
keys = [(o[0], o[1], o[2]) for o in out]
assert len(keys) == len(set(keys)), "duplicate keys"
for b, c, s, new in out:
    k = (b, c, s)
    assert k in cur, ("key not in report", k)
    assert new and "\n" not in new and "\t" not in new
    assert new != cur[k], ("unchanged", k)

# coverage: which report (book,chunk,seg) are missing from output
all_keys = []
for d in rows:
    k = (d["book"], d["chunk"], d["seg"])
    if k not in all_keys:
        all_keys.append(k)
missing = [k for k in all_keys if k not in set(keys)]
print("report segs:", len(all_keys), "output segs:", len(out), "missing:", len(missing))
for k in missing:
    n = sum(1 for d in rows if (d["book"], d["chunk"], d["seg"]) == k)
    print("  MISSING", k, "rows=", n)

print("\n==== changed spans (old => new) ====")
nchg = 0
for b, c, s, new in out:
    old = cur[(b, c, s)]
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    spans = [op for op in sm.get_opcodes() if op[0] != "equal"]
    nchg += len(spans)
    print("\n[%s %s %s] %d change(s), len %d->%d" % (b, c, s, len(spans), len(old), len(new)))
    for tag, i1, i2, j1, j2 in spans:
        pre = old[max(0, i1 - 12):i1]
        post = old[i2:i2 + 12]
        print("   ctx: ...%s[%s]=>[%s]%s..." % (pre, old[i1:i2], new[j1:j2], post))
print("\ntotal change spans:", nchg)
