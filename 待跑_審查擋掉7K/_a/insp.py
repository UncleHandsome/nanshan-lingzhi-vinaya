# -*- coding: utf-8 -*-
"""Dump 校閱_7K material vs current out for one or more file numbers."""
import os, io, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    lines = rd(os.path.join(X7, "校閱_%s.txt" % nnn)).replace("\r\n", "\n").split("\n")
    segs = []
    cur = None
    for ln in lines:
        m = re.match(r"^【(\d{3}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)),
                   "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:]
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:]
    return segs


def chunk_lines(chunk):
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    return lines, eol, p


def run(nnn):
    segs = parse_x7(nnn)
    buf = []
    cache = {}
    for s in segs:
        if s["chunk"] not in cache:
            cache[s["chunk"]] = chunk_lines(s["chunk"])
        lines, eol, p = cache[s["chunk"]]
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        cur = lines[idxs[s["idx"] - 1]].strip()
        same = (cur == s["tr"])
        buf.append("=== %s %s#%d %s" % (s["no"], s["chunk"], s["idx"], "SAME" if same else "CHANGED"))
        buf.append("[原] " + s["src"])
        buf.append("[材] " + s["tr"])
        if not same:
            buf.append("[現] " + cur)
        buf.append("")
    out = os.path.join(HERE, "ins_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
