# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _zx1_lib as L

for c, p in [("01e_上一上", 26), ("01e_上一上", 31), ("01e_上一上", 48), ("01f_上一上", 9), ("01f_上一上", 15)]:
    print("---", c, p)
    print(L.para(c, p))
