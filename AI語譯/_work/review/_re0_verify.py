# -*- coding: utf-8 -*-
import json, io, os, difflib
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(os.path.join(OUT, "rows.json"), encoding="utf-8"))
lines = []
stats = {"ok": 0, "punct": 0}
for r in rows:
    old, new = r["old"], r["new"]
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    ops = [(t, old[i1:i2], new[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
    bad = ""
    for badseq in ["。。", "，，", "，。", "、。", "：。", "；。", "（）"]:
        if badseq in new and badseq not in old:
            bad += " PUNCT:" + badseq
    if bad:
        stats["punct"] += 1
    lines.append("### %s %s#%-4d ratio=%.3f len %d->%d %s" % (
        r["book"], r["chunk"], r["seg"], sm.ratio(), len(old), len(new), bad))
    for t, a, b in ops[:4]:
        lines.append("   [%s] -%r" % (t, a[:120]))
        lines.append("        +%r" % (b[:120],))
    lines.append("")
io.open(os.path.join(OUT, "verify_diff.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("rows", len(rows), "punct-suspect", stats["punct"])
