# -*- coding: utf-8 -*-
"""ret3 04_比丘尼鈔：顯示 out 段（1-based index）與對應原典行，便於逐條核對。"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret3_lib as L


def srcpath(chunk):
    g = glob.glob(os.path.join(L.SRC, chunk + "_*.txt"))
    return g[0]


def srcparas(chunk):
    s = open(srcpath(chunk), encoding="utf-8-sig").read().replace("\r", "")
    body = s.split("========================", 1)[1]
    return [x.strip() for x in body.split("\n") if x.strip()]


def dump(chunk, lo, hi):
    p, t = L.load(chunk)
    ps = L.paras(t)
    sps = srcparas(chunk)
    print("FILE:", os.path.basename(p), "out paras:", len(ps), "src paras:", len(sps))
    for i in range(max(1, lo), min(len(ps), hi) + 1):
        print("\n===== OUT #%d (line %d) =====" % (i, L.line_of(t, i)))
        print(ps[i - 1])
        if i - 1 <= len(sps):
            print("--- SRC #%d ---" % i)
            print(sps[i - 1][:1200])


if __name__ == "__main__":
    dump(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
