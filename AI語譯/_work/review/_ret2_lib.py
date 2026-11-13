# -*- coding: utf-8 -*-
"""ret2 資持記 套用：段落級讀寫工具（保留 LF、段數不變）。"""
import os, sys, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "AI語譯", "out", "資持記")
SRC = os.path.join(ROOT, "TXT", "資持記")


def path(chunk):
    for n in os.listdir(OUT):
        if n.startswith(chunk + "_"):
            return os.path.join(OUT, n)
    raise FileNotFoundError(chunk)


def load(chunk):
    p = path(chunk)
    with open(p, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    return p, t


def paras(t):
    """段落 = 以 '\n\n' 分隔；回傳 list，最後可能為空字串（檔尾換行）。"""
    return t.split("\n\n")


def show(chunk, idx):
    p, t = load(chunk)
    ps = paras(t)
    print("FILE:", p)
    print("lines:", t.count("\n"), "paras:", len(ps), "CR:", t.count("\r"),
          "trailing:", repr(t[-3:]))
    if 1 <= idx <= len(ps):
        print("---- para %d (line %d) ----" % (idx, t[:sum(len(x)+2 for x in ps[:idx-1])].count("\n")+1))
        print(ps[idx-1])
    else:
        print("idx out of range")


def ctx(chunk, idx, before=2, after=2):
    p, t = load(chunk)
    ps = paras(t)
    lo = max(1, idx - before)
    hi = min(len(ps), idx + after)
    for i in range(lo, hi + 1):
        print("[%d] %s" % (i, ps[i-1][:400]))
        print()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        show(sys.argv[2], int(sys.argv[3]))
    elif cmd == "ctx":
        ctx(sys.argv[2], int(sys.argv[3]),
            int(sys.argv[4]) if len(sys.argv) > 4 else 2,
            int(sys.argv[5]) if len(sys.argv) > 5 else 2)
    elif cmd == "stat":
        for c in sys.argv[2:]:
            p, t = load(c)
            print("%s\tlines=%d\tparas=%d\tCR=%d\tbytes=%d" %
                  (os.path.basename(p), t.count("\n"), len(paras(t)), t.count("\r"),
                   os.path.getsize(p)))
