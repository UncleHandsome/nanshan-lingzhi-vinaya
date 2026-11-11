# -*- coding: utf-8 -*-
"""Build fix_r2_zhichi.tsv + stats from applied edit files (verified against backup)."""
import io, os, json, glob

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "資持記")
BAK = os.path.join(ROOT, "歸檔", "r2修正前", "資持記")
WORK = os.path.join(ROOT, "AI語譯", "_work", "review")

chunk = "01a_上一上"
new = [l for l in io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8").read().split("\n") if l.strip()]
old = [l for l in io.open(os.path.join(BAK, chunk + ".txt"), encoding="utf-8").read().split("\n") if l.strip()]
assert len(new) == len(old) == 65
changed = [i + 1 for i in range(65) if new[i] != old[i]]

reps = 0
segs_with_edits = 0
for p in sorted(glob.glob(os.path.join(WORK, "_r2z_edits_*.json"))):
    d = json.load(io.open(p, encoding="utf-8"))
    for e in d:
        if e["chunk"] != chunk:
            continue
        segs_with_edits += 1
        reps += len(e["reps"])
print("changed segs:", len(changed), "segs_with_edits:", segs_with_edits, "reps:", reps)
print("unchanged:", [i for i in range(1, 66) if i not in changed])

with io.open(os.path.join(WORK, "fix_r2_zhichi.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for s in changed:
        f.write("資持記\t%s\t%d\t%s\n" % (chunk, s, new[s - 1]))
print("tsv rows:", len(changed))
