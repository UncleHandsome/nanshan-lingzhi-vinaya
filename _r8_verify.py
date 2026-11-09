# -*- coding: utf-8 -*-
import json, io, difflib

rows = json.load(io.open("_r8_rows.json", encoding="utf-8"))
base = {}
for r in rows:
    base.setdefault((r["chunk"], r["seg"]), r["current"])

out = []
with io.open("AI語譯/_work/review/fix_r8_g1.tsv", encoding="utf-8") as f:
    for ln in f:
        ln = ln.rstrip("\n")
        if not ln:
            continue
        p = ln.split("\t")
        assert len(p) == 4, p[:2]
        out.append(p)

print("rows", len(out), "unique", len(set((p[1], p[2]) for p in out)))
for b, c, s, t in out:
    assert b == "03_業疏"
    cur = base[(c, s)]
    # char-level diff hunks
    sm = difflib.SequenceMatcher(None, cur, t, autojunk=False)
    hunks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        ctx_b = cur[max(0, i1 - 12):i1]
        ctx_a = cur[i2:i2 + 12]
        hunks.append("%s …%s[[%s]]%s…" % (tag, ctx_b, cur[i1:i2], ctx_a))
    print("\n%s seg=%s" % (c, s))
    for h in hunks:
        print("   ", h)
    print("    NEW:", t[:0])
