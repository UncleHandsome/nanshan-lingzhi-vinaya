# -*- coding: utf-8 -*-
import pymupdf, os
B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
for p in [B + r"\歸檔\合編備份_卷中之二\行事鈔資持記句級合編_卷中之二.pdf", B + r"\白話\PDF\行事鈔資持記句級合編_卷中之二.pdf"]:
    d = pymupdf.open(p)
    print(os.path.basename(os.path.dirname(p)), d.page_count, os.path.getsize(p))
    d.close()
