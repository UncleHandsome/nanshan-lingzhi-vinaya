# -*- coding: utf-8 -*-
"""condensed view for 否決複審 (02_戒疏 卷一上之一 續, 18 chunks)
  python _rv18_kit.py show 454 458 ...
"""
import os, sys, re, io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv18_view")
BOOK = "02_戒疏"


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2).split("/", 1)[1],
                   "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:].strip()
    return segs


_cache = {}


def read_chunk(chunk):
    if chunk in _cache:
        return _cache[chunk]
    p = os.path.join(OUT, BOOK, chunk + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    _cache[chunk] = (raw, eol, lines, idxs, p)
    return _cache[chunk]


def cur_of(seg):
    raw, eol, lines, idxs, p = read_chunk(seg["chunk"])
    return lines[idxs[seg["idx"] - 1]].strip()


def diffspan(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, a[max(0, i - 8):len(a) - j + 8], b[max(0, i - 8):len(b) - j + 8]


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("@@@@ resp_%s @@@@" % nnn)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("@@@@ segs %s (%d) @@@@" % (nnn, len(segs)))
    for s in segs:
        try:
            c = cur_of(s)
        except FileNotFoundError:
            buf.append("■ %s #%d  [他卷段，chunk %s 不在本卷]"
                       % (s["no"], s["idx"], s["chunk"]))
            buf.append("  原：" + s["src"])
            continue
        if c == s["tr"]:
            buf.append("■ %s #%d" % (s["no"], s["idx"]))
        else:
            buf.append("■ %s #%d [改]" % (s["no"], s["idx"]))
        buf.append("  原：" + s["src"])
        buf.append("  譯：" + c)
        if c != s["tr"]:
            _, oa, ob = diffspan(s["tr"], c)
            buf.append("  差：" + oa + " → " + ob)
    out = os.path.join(VIEW, "v_%s.txt" % nnn)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    for n in sys.argv[2:]:
        show(n)
