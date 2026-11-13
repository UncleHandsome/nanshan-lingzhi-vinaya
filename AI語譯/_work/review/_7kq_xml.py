# -*- coding: utf-8 -*-
"""把 _src/xml 的 TEI XML 轉為可搜尋純文字（保留卷/科段落）。"""
import re, io, os, sys, xml.etree.ElementTree as ET

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"

def convert(name, out):
    p = os.path.join(ROOT, "_src", "xml", name + ".xml")
    txt = io.open(p, encoding="utf-8").read()
    # 去標籤，保留段落
    txt = re.sub(r"<lb[^>]*/>", "\n", txt)
    txt = re.sub(r"<pb[^>]*/>", "\n", txt)
    txt = re.sub(r"</p>", "\n", txt)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = re.sub(r"&amp;", "&", txt)
    txt = re.sub(r"\n{2,}", "\n", txt)
    io.open(os.path.join(ROOT, model_out), "w", encoding="utf-8", newline="").write(txt)

if __name__ == "__main__":
    for name, model_out in [("X39n0714", "_7kq_xingzong1.txt"), ("X40n0714", "_7kq_xingzong2.txt")]:
        convert(name, model_out)
        print("done", model_out, os.path.getsize(os.path.join(ROOT, model_out)))
