# -*- coding: utf-8 -*-
"""Build mapping: material file -> [(segid, book, chunk, segno)], three books only.
Also verify paragraph index against AI語譯/out/<book>/<chunk>.txt.
"""
import io, os, re, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
OUTD = os.path.join(ROOT, "AI語譯", "out")
BOOKS = ("03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔")

def read_norm(book, chunk):
    p = os.path.join(OUTD, book, chunk + ".txt")
    if not os.path.exists(p):
        return None, None
    raw = io.open(p, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    t = raw.replace("\r\n", "\n")
    return t, eol


def paras(book, chunk):
    t, _ = read_norm(book, chunk)
    if t is None:
        return None
    ps = t.split("\n\n")
    if ps and ps[-1].endswith("\n"):
        ps[-1] = ps[-1][:-1]
    return ps

def main():
    files = {}
    for fn in sorted(os.listdir(MAT)):
        if not fn.startswith("校閱_"):
            continue
        n = int(re.sub(r"\D", "", fn))
        if n < 1393:
            continue
        t = io.open(os.path.join(MAT, fn), encoding="utf-8").read()
        segs = []
        for m in re.finditer(r"【(\d{4}-\d{4})】([^\r\n/]+)/([^#\r\n]+)#(\d+)", t):
            segs.append((m.group(1), m.group(2).strip(), m.group(3).strip(), int(m.group(4))))
        if not segs:
            continue
        if not any(s[1] in BOOKS for s in segs):
            continue
        files[n] = segs
    # verify out paragraph counts
    cache = {}
    bad = []
    stat = {}
    for n, segs in files.items():
        for sid, book, chunk, seg in segs:
            if book not in BOOKS:
                continue
            key = (book, chunk)
            if key not in cache:
                cache[key] = paras(book, chunk)
            ps = cache[key]
            stat.setdefault(book, set()).add(chunk)
            if ps is None:
                bad.append((n, sid, book, chunk, seg, "NOFILE"))
            elif seg > len(ps):
                bad.append((n, sid, book, chunk, seg, "SEG>%d" % len(ps)))
    print("material files:", len(files))
    print("range:", min(files), max(files))
    for b in BOOKS:
        print(" ", b, "chunks:", len(stat.get(b, [])))
    print("bad:", len(bad))
    for x in bad[:20]:
        print("  ", x)
    json.dump({str(k): v for k, v in files.items()},
              io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2o_map.json"), "w", encoding="utf-8"),
              ensure_ascii=False)

if __name__ == "__main__":
    main()
