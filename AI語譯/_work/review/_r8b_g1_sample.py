# -*- coding: utf-8 -*-
import io, os
base = os.path.dirname(os.path.abspath(__file__))
lines = [l for l in io.open(os.path.join(base, "fix_r8b_g1.tsv"), encoding="utf-8").read().split("\n") if l.strip()]
out = io.open(os.path.join(base, "_r8b_g1_out_sample.txt"), "w", encoding="utf-8")
want = [("02b_卷上之二", "1"), ("04a_卷中之二", "11"), ("04b_卷中之二", "30"), ("03a_卷中之一", "4")]
for l in lines:
    f = l.split("\t")
    if (f[1], f[2]) in want:
        out.write("=== %s | %s | seg %s | len %d\n%s\n\n" % (f[0], f[1], f[2], len(f[3]), f[3]))
out.close()
print("ok")
