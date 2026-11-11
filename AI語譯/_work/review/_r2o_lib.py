# -*- coding: utf-8 -*-
"""Lib for r2 other-three-books work: read/write out chunks, backup, show segs."""
import io, os, re, json, shutil, datetime

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "r2修正前")
WK = os.path.join(ROOT, "AI語譯", "_work", "review")


def read(book, chunk):
    p = os.path.join(OUTD, book, chunk + ".txt")
    raw = io.open(p, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol, p


def paras(book, chunk):
    t, eol, p = read(book, chunk)
    ps = t.split("\n\n")
    if ps and ps[-1].endswith("\n"):
        ps[-1] = ps[-1][:-1]
    return ps


def write(book, chunk, ps):
    t, old_eol, p = read(book, chunk)
    had_nl = t.endswith("\n")
    text = "\n\n".join(ps)
    if had_nl and not text.endswith("\n"):
        text += "\n"
    text = text.replace("\n", old_eol)
    io.open(p, "w", encoding="utf-8", newline="").write(text)


def backup(book, chunk):
    src = os.path.join(OUTD, book, chunk + ".txt")
    d = os.path.join(BAK, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + ".txt")
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        return dst
    return None


def src_index():
    return json.load(io.open(os.path.join(WK, "_r2o_src.json"), encoding="utf-8"))


def show(book, chunk, seg, width=2000):
    ps = paras(book, chunk)
    src = src_index().get(book, {}).get(chunk, {})
    print("=" * 70)
    print("%s/%s #%d  (paras=%d)" % (book, chunk, seg, len(ps)))
    s = src.get(str(seg), "<NO SRC>")
    print("【原文】" + s[:width * 2])
    print("-" * 70)
    print("【譯文】" + ps[seg - 1][:width * 3])


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        show(sys.argv[1], sys.argv[2], int(sys.argv[3]))
