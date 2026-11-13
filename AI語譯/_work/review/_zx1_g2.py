# -*- coding: utf-8 -*-
import io
p = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\資持記\01_上一上.txt"
lines = io.open(p, encoding="utf-8").read().split("\n")
print("total lines", len(lines))
print("".join(lines[36:78]))
