# -*- coding: utf-8 -*-
"""7K 資持記 下三_c helpers (1989-1995)."""
import os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out", "資持記")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_d3c_view")


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def norm(t):
    return t.replace("\r\n", "\n").replace("\r", "\n")


def read_out(chunk):
    raw = read(os.path.join(OUT, chunk + ".txt"))
    eol = "\r\n" if "\r\n" in raw else ("\r" if "\r" in raw else "\n")
    lines = norm(raw).split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines, eol


def mat_map(n):
    t = norm(read(os.path.join(MAT, "校閱_%d.txt" % n)))
    items = []
    pat = re.compile(r"【(\d{4}-\d{4})】資持記/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【\d{4}-\d{4}】|\s*\Z)", re.S)
    for m in pat.finditer(t):
        items.append(dict(seg=m.group(1), chunk=m.group(2), idx=int(m.group(3)),
                          src=m.group(4).strip(), tr=m.group(5).strip()))
    return items


def para(lines):
    return [(i, l) for i, l in enumerate(lines) if l.strip()]


def locate(items, chunk, cache=None):
    """Return list of (item, out_no, note) matching by text, tolerating +-1 shift."""
    if cache is None:
        cache = {}
    if chunk not in cache:
        cache[chunk] = read_out(chunk)[0]
    lines = cache[chunk]
    ne = [l.strip() for l in lines if l.strip()]
    out = []
    for it in items:
        k = it["idx"]
        note = ""
        no = None
        cands = [k - 1, k, k - 2, k + 1]
        for c in cands:
            if 0 <= c < len(ne):
                if ne[c] == it["tr"]:
                    no = c + 1
                    note = "exact"
                    break
        if no is None:
            # prefix / substring relation
            best = None
            for c in cands:
                if 0 <= c < len(ne):
                    cur = ne[c]
                    if it["tr"].startswith(cur) or cur.startswith(it["tr"]):
                        score = len(os.path.commonprefix([cur, it["tr"]]))
                        if best is None or score > best[0]:
                            best = (score, c)
            if best:
                no = best[1] + 1
                note = "partial"
                if ne[no - 1] != it["tr"]:
                    note += " span"
        out.append((it, no, note))
    return out, cache
