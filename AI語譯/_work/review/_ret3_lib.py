# -*- coding: utf-8 -*-
"""ret3 04_比丘尼鈔 套用：段落級讀寫工具（保留原行尾、段數不變）。"""
import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "AI語譯", "out", "04_比丘尼鈔")
SRC = os.path.join(ROOT, "TXT_分卷", "04_比丘尼鈔")


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
    return t.split("\n\n")


def line_of(t, idx):
    ps = paras(t)
    return t[:sum(len(x) + 2 for x in ps[:idx - 1])].count("\n") + 1


def show(chunk, idx):
    p, t = load(chunk)
    ps = paras(t)
    print("FILE:", os.path.basename(p))
    print("lines:", t.count("\n"), "paras:", len(ps), "CR:", t.count("\r"),
          "trailing:", repr(t[-3:]))
    if 1 <= idx <= len(ps):
        print("---- para %d (line %d) len=%d ----" % (idx, line_of(t, idx), len(ps[idx - 1])))
        print(ps[idx - 1])
    else:
        print("idx out of range")


def find(chunk, needle, width=200):
    p, t = load(chunk)
    ps = paras(t)
    hits = [(i + 1, x) for i, x in enumerate(ps) if needle in x]
    print("FILE:", os.path.basename(p), "paras:", len(ps))
    for i, x in hits:
        k = x.find(needle)
        print("[%d] ...%s..." % (i, x[max(0, k - width): k + len(needle) + width]))
        print()


def stat(chunks):
    for c in chunks:
        p, t = load(c)
        print("%s\tlines=%d\tparas=%d\tCR=%d\tbytes=%d" %
              (os.path.basename(p), t.count("\n"), len(paras(t)), t.count("\r"),
               os.path.getsize(p)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        show(sys.argv[2], int(sys.argv[3]))
    elif cmd == "find":
        find(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 200)
    elif cmd == "stat":
        stat(sys.argv[2:])
