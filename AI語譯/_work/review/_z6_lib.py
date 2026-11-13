# -*- coding: utf-8 -*-
"""7K 資持記 中一上 校閱輔助：材料讀取、段落級替換、備份、驗證。"""
import io
import json
import os
import re
import shutil
import sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = "資持記"
OUTDIR = os.path.join(ROOT, "AI語譯", "out", BOOK)
MATDIR = os.path.join(ROOT, "校閱_7K")
BAKDIR = os.path.join(ROOT, "歸檔", "7K卷修正前", BOOK)

SEG_RE = re.compile(r"^【(\d{4})-(\d{4})】(?:.+?)/(\S+?)#(\d+)\s*$")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def mat(n):
    t = rd(os.path.join(MATDIR, u"校閱_%d.txt" % n))
    segs = []
    cur = None
    buf = {"原文": [], "譯文": []}

    def flush():
        if cur is not None:
            cur["orig"] = "\n".join(buf["原文"]).strip()
            cur["trans"] = "\n".join(buf["譯文"]).strip()
            segs.append(cur)

    for ln in t.split("\n"):
        m = SEG_RE.match(ln.strip())
        if m:
            flush()
            cur = {"idx": m.group(1), "seg": m.group(2),
                   "chunk": m.group(3), "para": int(m.group(4))}
            buf = {"原文": [], "譯文": []}
            continue
        if cur is None:
            continue
        s = ln.strip()
        if s.startswith("【原文】"):
            buf["原文"].append(s[len("【原文】"):])
        elif s.startswith("【譯文】"):
            buf["譯文"].append(s[len("【譯文】"):])
        elif s:
            if buf["原文"] and not buf["譯文"]:
                buf["原文"].append(s)
            else:
                buf["譯文"].append(s)
    flush()
    return segs


def sep(t):
    return "\r\n\r\n" if "\r\n" in t else "\n\n"


def paras(chunk):
    t = rd(os.path.join(OUTDIR, chunk + ".txt"))
    return t, sep(t)


def para(chunk, n):
    t, s = paras(chunk)
    return t.split(s)[n - 1]


def backup(chunk):
    os.makedirs(BAKDIR, exist_ok=True)
    dst = os.path.join(BAKDIR, chunk + "_v.txt")
    if os.path.exists(dst):
        return False
    shutil.copyfile(os.path.join(OUTDIR, chunk + ".txt"), dst)
    return True


def apply_edits(chunk, edits, dry=False):
    """edits: list of dict(para=int, old=str, new=str, note=str)."""
    t, s = paras(chunk)
    ps = t.split(s)
    cnt = 0
    for e in edits:
        i = e["para"] - 1
        if not (0 <= i < len(ps)):
            raise SystemExit("BAD para %s#%d" % (chunk, e["para"]))
        n = ps[i].count(e["old"])
        if n != 1:
            raise SystemExit("HIT %d %s#%d old=%r" % (n, chunk, e["para"], e["old"][:40]))
        ps[i] = ps[i].replace(e["old"], e["new"])
        cnt += 1
    if dry:
        return cnt
    backup(chunk)
    wr(os.path.join(OUTDIR, chunk + ".txt"), s.join(ps))
    return cnt


def verify(chunk, before):
    t, s = paras(chunk)
    ps = t.split(s)
    bp, bn = before
    return (len(bp.split(s)) == len(ps), bn)


def snapshot(chunk):
    t = rd(os.path.join(OUTDIR, chunk + ".txt"))
    return (t, t.count("\n"))


def show(n, chunk=None, only_idx=None):
    segs = mat(n)
    out = []
    for s in segs:
        if only_idx and s["idx"] != only_idx:
            continue
        cur = para(s["chunk"], s["para"])
        same = "SAME" if cur.strip() == s["trans"].strip() else "DIFF"
        out.append(u"%s %s#%d [%s] outlen=%d matlen=%d" % (
            s["idx"], s["chunk"], s["para"], same, len(cur), len(s["trans"])))
    return "\n".join(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        print(show(int(sys.argv[2])))
    elif cmd == "dump":
        n = int(sys.argv[2])
        for s in mat(n):
            print(u"=== %s %s#%d ===" % (s["idx"], s["chunk"], s["para"]))
            print(u"[原] " + s["orig"])
            cur = para(s["chunk"], s["para"])
            print(u"[現] " + cur)
