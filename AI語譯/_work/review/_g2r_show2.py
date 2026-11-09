# -*- coding: utf-8 -*-
import csv, os

BASE = r"AI語譯\_work\review"
out = {}
with open(os.path.join(BASE, "fix_re5_g2.tsv"), encoding="utf-8", newline="") as f:
    for ln in f:
        b, c, s, t = ln.rstrip("\n").split("\t")
        out[(b, c, s)] = t

shown = {
    ("03_業疏", "17b_卷三之六", "124"), ("03_業疏", "18a_卷四之一", "7"),
    ("03_業疏", "18a_卷四之一", "20"), ("03_業疏", "18a_卷四之一", "75"),
    ("03_業疏", "18b_卷四之一", "64"), ("03_業疏", "18b_卷四之一", "80"),
    ("03_業疏", "18b_卷四之一", "85"), ("資持記", "14a_下二", "28"),
    ("資持記", "14a_下二", "29"), ("資持記", "14a_下二", "30"),
    ("資持記", "14a_下二", "31"), ("資持記", "13b_下一", "43"),
    ("資持記", "14b_下二", "37"),
}
for k, t in out.items():
    if k in shown:
        continue
    if len(t) > 600:
        continue
    print("\n=== %s %s %s (%d)" % (k[0], k[1], k[2], len(t)))
    print(t)

# long segments: print +-70 chars around each edit marker
MARK = {
    ("01_行事鈔", "09a_卷下之一", "32"): ["半邊朝上", "借充代用"],
    ("01_行事鈔", "09a_卷下之一", "43"): ["不增益布縷邊的尼師壇是合法的", "非法妄行"],
    ("01_行事鈔", "10a_卷下之二", "8"): ["如同食用米飯", "不令粗"],
}
print("\n\n=== long segments, edit context ===")
for k, marks in MARK.items():
    t = out[k]
    for m in marks:
        i = t.find(m)
        print("\n[%s %s %s] marker %r at %d" % (k[0], k[1], k[2], m, i))
        print("  ...%s..." % t[max(0, i - 70):i + len(m) + 70])
