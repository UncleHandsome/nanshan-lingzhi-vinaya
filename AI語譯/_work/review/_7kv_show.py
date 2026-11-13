# -*- coding: utf-8 -*-
"""工作用：抽出 chunk 某段的字串片段（供精確 old/new 比對）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7kv_lib as L

def seg_text(chunk, seg):
    pm = L.chunk_paras(chunk)[3]
    return pm[seg - 1][1]

def show(chunk, seg, start=None, end=None, width=None):
    t = seg_text(chunk, seg)
    a = 0 if start is None else t.find(start)
    if start is not None and a < 0:
        print("!! start not found:", start)
        return
    b = len(t) if end is None else t.find(end, a)
    if end is not None and b < 0:
        print("!! end not found:", end)
        return
    b = b + len(end) if end else len(t)
    print(t[a:b])

if __name__ == "__main__":
    chunk, seg = sys.argv[1], int(sys.argv[2])
    if len(sys.argv) > 3:
        show(chunk, seg, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        print(seg_text(chunk, seg))
