# -*- coding: utf-8 -*-
import csv, os, sys

BASE = r"AI語譯\_work\review"
out = {}
with open(os.path.join(BASE, "fix_re5_g2.tsv"), encoding="utf-8", newline="") as f:
    for ln in f:
        b, c, s, t = ln.rstrip("\n").split("\t")
        out[(b, c, s)] = t

want = [
    ("03_業疏", "17b_卷三之六", "124"),
    ("03_業疏", "18a_卷四之一", "7"),
    ("03_業疏", "18a_卷四之一", "20"),
    ("03_業疏", "18a_卷四之一", "75"),
    ("03_業疏", "18b_卷四之一", "64"),
    ("03_業疏", "18b_卷四之一", "80"),
    ("03_業疏", "18b_卷四之一", "85"),
    ("資持記", "14a_下二", "28"),
    ("資持記", "14a_下二", "29"),
    ("資持記", "14a_下二", "30"),
    ("資持記", "14a_下二", "31"),
    ("資持記", "13b_下一", "43"),
    ("資持記", "14b_下二", "37"),
]
for k in want:
    t = out[k]
    print("\n=== %s %s %s  (len %d)" % (k[0], k[1], k[2], len(t)))
    print(t)

# quote-balance report on all changed segments
print("\n\n=== quote balance (「 vs 」, （ vs ）, 〔 vs 〕) ===")
for k, t in out.items():
    a, b = t.count("「"), t.count("」")
    c1, c2 = t.count("（"), t.count("）")
    d1, d2 = t.count("〔"), t.count("〕")
    if a != b or c1 != c2 or d1 != d2:
        print("UNBALANCED", k, "「」=%d/%d （）=%d/%d 〔〕=%d/%d" % (a, b, c1, c2, d1, d2))
print("done")
