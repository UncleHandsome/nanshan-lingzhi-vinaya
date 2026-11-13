# -*- coding: utf-8 -*-
"""定位現行 out 檔的行 → 段號（用校閱_7K 的段序，依 chunk 檔名分組）。
用法: python _rv2_map.py 10d "字串1" "字串2" ...
"""
import os, sys, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of, read_chunk  # noqa

OUT = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")


def seglist(fname):
    L = []
    for n in range(844, 895):
        for s in parse_x7(str(n)):
            if s["chunk"] == fname:
                L.append(s)
    return L


def where(fname, needle):
    raw, eol, lines, idxs, p = read_chunk(fname)
    L = seglist(fname)
    hits = [i for i, l in enumerate(lines) if needle in l]
    for i in hits:
        # 非空行序
        k = sum(1 for j in idxs if j < i)
        seg = L[k] if k < len(L) else None
        # 驗證
        ok = ""
        if seg:
            c = cur_of(seg)
            ok = "OK" if needle in c else "?(現行無)"
        print("%s line=%d -> %s %s" % (fname, i + 1, seg["no"] if seg else "(超出)", ok))


if __name__ == "__main__":
    fname = sys.argv[1]
    for n in sys.argv[2:]:
        where(fname, n)
