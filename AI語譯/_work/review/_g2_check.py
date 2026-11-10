# -*- coding: utf-8 -*-
import io
lines = io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n")
print("rows", len([l for l in lines if l.strip()]))
for l in lines:
    if not l.strip():
        continue
    f = l.split("\t")
    if len(f) != 4:
        print("BADFIELDS", len(f), f[0])
        continue
    book, chunk, seg, new = f
    issues = []
    if new.count("「") != new.count("」"):
        issues.append("corner %d/%d" % (new.count("「"), new.count("」")))
    if new.count("『") != new.count("』"):
        issues.append("double %d/%d" % (new.count("『"), new.count("』")))
    if "（或" in new or "或：" in new:
        issues.append("ALT")
    if "『" in new:
        issues.append("SHUANG")
    if issues:
        print("%s %s s%s: %s" % (book, chunk, seg, "; ".join(issues)))
