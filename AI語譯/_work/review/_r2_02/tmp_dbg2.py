# -*- coding: utf-8 -*-
import os, glob, re, io
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
J10=os.path.join(ROOT,"校閱_10K")
print("dir exists", os.path.isdir(J10))
g=glob.glob(os.path.join(J10,"*.txt"))
print("glob star", len(g))
g2=glob.glob(os.path.join(J10,"校閱_*.txt"))
print("glob cn", len(g2))
print("listdir", len(os.listdir(J10)))
print("sample", os.listdir(J10)[:3])
p=os.path.join(J10,"校閱_642.txt")
print("642 exists", os.path.exists(p))
t=io.open(p,encoding="utf-8-sig",errors="replace").read()
print("len", len(t))
print(t[:300])
