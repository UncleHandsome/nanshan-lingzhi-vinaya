# -*- coding: utf-8 -*-
"""ret3 套用（05/資持/01）：段落讀寫、顯示、套用、驗證。"""
import io
import json
import os
import sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")
BOOKDIR = {
    "05": "05_拾毗尼義鈔",
    "資持記": "資持記",
    "01": "01_行事鈔",
}


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def sep(t):
    return "\r\n\r\n" if "\r\n" in t else "\n\n"


def path(book, chunk):
    return os.path.join(OUT, BOOKDIR[book], chunk + ".txt")


def parts(book, chunk):
    t = rd(path(book, chunk))
    return t, sep(t), t.split(sep(t))


def para(book, chunk, n):
    t, s, ps = parts(book, chunk)
    return ps[n - 1]


def apply(edits):
    """edits: list of dict(book, chunk, para, old, new). 精確取代，驗證必中且唯一。"""
    byfile = {}
    for e in edits:
        byfile.setdefault((e["book"], e["chunk"]), []).append(e)
    report = []
    for (book, chunk), es in byfile.items():
        t, s, ps = parts(book, chunk)
        before = len(ps)
        for e in es:
            i = e["para"] - 1
            old, new = e["old"], e["new"]
            c = ps[i].count(old)
            if c != 1:
                raise SystemExit(u"命中數異常 %s#%d count=%d old=%r" % (chunk, e["para"], c, old))
            ps[i] = ps[i].replace(old, new)
            report.append(u"%s#%d %d字->%d字" % (chunk, e["para"], len(old), len(new)))
        out = s.join(ps)
        wr(path(book, chunk), out)
        t2, s2, ps2 = parts(book, chunk)
        assert len(ps2) == before, "段數變動 " + chunk
    return report


def stat(book, chunk):
    t, s, ps = parts(book, chunk)
    return len(ps), t.count("\n"), t.count("\r")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        book, chunk = sys.argv[2], sys.argv[3]
        for n in [int(x) for x in sys.argv[4:]]:
            t, s, ps = parts(book, chunk)
            print(u"=== %s %s #%d ===" % (book, chunk, n))
            print(ps[n - 1])
            print()
    elif cmd == "len":
        book, chunk = sys.argv[2], sys.argv[3]
        t, s, ps = parts(book, chunk)
        print(len(ps), "段", t.count("\n"), "換行", "CR=", t.count("\r"))
    elif cmd == "apply":
        dat = json.load(io.open(sys.argv[2], encoding="utf-8"))
        for r in apply(dat):
            print(r)
    elif cmd == "stat":
        for book in ("05", "資持記", "01"):
            d = os.path.join(OUT, BOOKDIR[book])
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".txt"):
                    n, ln, cr = stat(book, fn[:-4])
                    print(book, fn, n, "段", ln, "行", "CR=%d" % cr)
