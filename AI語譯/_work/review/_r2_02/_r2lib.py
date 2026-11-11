# -*- coding: utf-8 -*-
"""Helpers: locate/read/write out paragraphs; load r2 mapping."""
import io, os, re, json
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT,"AI語譯","out","02_戒疏")

def path(chunk): return os.path.join(OUTD, chunk+".txt")

def read_raw(chunk):
    return io.open(path(chunk), encoding="utf-8", newline="").read()

def paras(chunk):
    t = read_raw(chunk)
    parts = t.split("\r\n\r\n")
    if parts and parts[-1].endswith("\r\n"):
        parts[-1] = parts[-1][:-2]
    return parts

def write_paras(chunk, ps):
    t = "\r\n\r\n".join(ps) + "\r\n"
    io.open(path(chunk),"w",encoding="utf-8",newline="").write(t)

def load_map():
    M = json.load(io.open(os.path.join(ROOT,"AI語譯","_work","review","_r2_02","_map.json"),encoding="utf-8"))
    return M
