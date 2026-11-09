# -*- coding: utf-8 -*-
import os, sys, textwrap
D = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1\seg"
name = sys.argv[1]
p = os.path.join(D, name + ".txt")
s = open(p, encoding="utf-8").read()
lines = [s[i:i+600] for i in range(0, len(s), 600)]
q = os.path.join(D, "_wrap_" + name + ".txt")
open(q, "w", encoding="utf-8").write("\n".join("%03d| %s" % (i+1, ln) for i, ln in enumerate(lines)))
print(q)
