# -*- coding: utf-8 -*-
"""裁定套用_資持記 輔助：段落讀取、比對、套用（驗 old 恰一次、段數不變）。"""
import io
import os
import shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = u"資持記"
OUTDIR = os.path.join(ROOT, "AI語譯", "out", BOOK)
BAKDIR = os.path.join(ROOT, "歸檔", "7K卷修正前", BOOK)


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def resolve(chunk):
    """chunk 可為 '16d' 或 '16d_下四'；回傳實際檔名（不含 .txt）。"""
    if os.path.exists(os.path.join(OUTDIR, chunk + ".txt")):
        return chunk
    hits = [f[:-4] for f in os.listdir(OUTDIR)
            if f.endswith(".txt") and f.split("_")[0] == chunk]
    if len(hits) != 1:
        raise SystemExit("BAD chunk %r -> %r" % (chunk, hits))
    return hits[0]


def path(chunk):
    return os.path.join(OUTDIR, resolve(chunk) + ".txt")


def paras(chunk):
    t = rd(path(chunk))
    s = "\r\n\r\n" if "\r\n" in t else "\n\n"
    return t, s


def para(chunk, n):
    t, s = paras(chunk)
    ps = t.split(s)
    if not (1 <= n <= len(ps)):
        raise SystemExit("BAD para %s#%d (max %d)" % (chunk, n, len(ps)))
    return ps[n - 1]


def idx(chunk):
    t, s = paras(chunk)
    return len(t.split(s)), t.count("\n")


def find(chunk, needle):
    t, s = paras(chunk)
    return [i + 1 for i, p in enumerate(t.split(s)) if needle in p]


def grep_all(needle, chunks=None):
    res = []
    files = chunks or sorted(f[:-4] for f in os.listdir(OUTDIR) if f.endswith(".txt"))
    for c in files:
        for i in find(c, needle):
            res.append((c, i))
    return res


def apply(chunk, edits, dry=False):
    """edits: list of dict(para=int, old=str, new=str)"""
    t, s = paras(chunk)
    ps = t.split(s)
    n0 = len(ps)
    log = []
    for e in edits:
        i = e["para"] - 1
        if not (0 <= i < len(ps)):
            raise SystemExit("BAD para %s#%d" % (chunk, e["para"]))
        cnt = ps[i].count(e["old"])
        if cnt != 1:
            raise SystemExit("HIT %d %s#%d old=%r" % (cnt, chunk, e["para"], e["old"][:60]))
        ps[i] = ps[i].replace(e["old"], e["new"])
        log.append(e)
    if dry:
        return len(log)
    if not os.path.exists(BAKDIR):
        os.makedirs(BAKDIR)
    dst = os.path.join(BAKDIR, chunk + "_v.txt")
    if not os.path.exists(dst):
        shutil.copyfile(path(chunk), dst)
    wr(path(chunk), s.join(ps))
    t2, s2 = paras(chunk)
    if len(t2.split(s2)) != n0:
        raise SystemExit("PARA COUNT CHANGED %s" % chunk)
    return len(log)
