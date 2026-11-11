# -*- coding: utf-8 -*-
"""Verify: paragraph counts, newline style, diffs only in logged segments, show old->new sentences."""
import io, os, json, re, difflib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
BAK = os.path.join(ROOT, "歸檔", "潤飾覆核前", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
log = json.load(io.open(os.path.join(HERE, "apply_log.json"), encoding="utf-8"))
changed = log["changed"]

def read(p):
    raw = io.open(p, encoding="utf-8", newline="").read()
    return raw

bad = []
report = []
for ch, segs in sorted(changed.items()):
    fn = ch + ".txt"
    if not os.path.exists(os.path.join(OUTD, fn)):
        bad.append("missing file %s" % fn); continue
    bp = os.path.join(BAK, fn[:-4] + "_p.txt")
    raw = read(os.path.join(OUTD, fn))
    old = read(bp)
    sep = "\r\n\r\n" if "\r\n" in raw else "\n\n"
    nl = "\r\n" if "\r\n" in raw else "\n"
    ps_new = raw.split(sep)
    ps_old = old.split(sep)
    if len(ps_new) != len(ps_old):
        bad.append("%s para count %d -> %d" % (fn, len(ps_old), len(ps_new)))
        continue
    # line endings
    if raw.replace("\r\n", "").count("\n") != 0:
        bad.append("%s LF-only present" % fn)
    diff = [i + 1 for i, (a, b) in enumerate(zip(ps_old, ps_new)) if a != b]
    if diff != sorted(segs):
        bad.append("%s diff segs %s != logged %s" % (fn, diff, sorted(segs)))
    for s in diff:
        a, b = ps_old[s - 1], ps_new[s - 1]
        sm = difflib.SequenceMatcher(None, a, b)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                report.append("%s#%d  %s => %s | ...%s..." % (ch[:3], s, a[i1:i2], b[j1:j2], b[max(0, j1 - 25):j2 + 25]))

print("files", len(changed), "paras", sum(len(v) for v in changed.values()), "bad", len(bad))
for x in bad: print("  BAD", x)
io.open(os.path.join(HERE, "diff.txt"), "w", encoding="utf-8").write("\n".join(report))
print("diff lines", len(report))
