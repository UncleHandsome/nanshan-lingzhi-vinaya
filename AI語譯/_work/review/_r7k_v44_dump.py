# -*- coding: utf-8 -*-
"""Dump 7K 卷四之四 (2761-2778) material + opinions into view files."""
import os, re, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_v44")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
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
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    _cache[chunk] = (raw, eol, lines, idxs, p)
    return _cache[chunk]


def diffspan(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, a[max(0, i - 10):len(a) - j + 10], b[max(0, i - 10):len(b) - j + 10]


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("#" * 20 + " 意見 resp_%s " % nnn + "#" * 20)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("#" * 20 + " 段落 %s（%d 段）" % (nnn, len(segs)) + "#" * 20)
    cur_chunk = None
    for s in segs:
        if s["chunk"] != cur_chunk:
            cur_chunk = s["chunk"]
            raw, eol, lines, idxs, p = read_chunk(cur_chunk)
            buf.append("\n@@ chunk = %s  (EOL=%s, 非空行=%d)" % (cur_chunk, eol == "\r\n" and "CRLF" or "LF", len(idxs)))
        i = idxs[s["idx"] - 1]
        c = lines[i].strip()
        same = (c == s["tr"])
        buf.append("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[材料譯文] " + s["tr"])
        if not same:
            pos, x, y = diffspan(s["tr"], c)
            buf.append("[現行譯文] " + c)
            buf.append("[差異@%d] 材料…%s… / 現行…%s…" % (pos, x, y))
    out = os.path.join(VIEW, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    return out


if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 2761
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 2778
    for n in range(a, b + 1):
        print(show(n))
