# -*- coding: utf-8 -*-
import sys, os
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\資持記\分冊\資持記_卷中.txt"
t = open(p, encoding="utf-8-sig").read().replace("\r\n", "\n")
needle = sys.argv[1]
i = t.find(needle)
print("idx", i)
back = int(sys.argv[2]) if len(sys.argv) > 2 else 200
fwd = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
open(os.path.join(os.path.dirname(__file__), "_v4_w.txt"), "w", encoding="utf-8").write(t[max(0,i-back):i+fwd])
print("ok")
