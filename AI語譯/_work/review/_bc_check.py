# -*- coding: utf-8 -*-
import re, io, os

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    lines = rd(os.path.join(X7, "校閱_%s.txt" % nnn)).replace("\r\n", "\n").split("\n")
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


def chunkfile(chunk):
    book, name = chunk.split("/", 1)
    return os.path.join(OUT, book, name + ".txt")


def current(chunk, idx):
    raw = rd(chunkfile(chunk))
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return lines[idxs[idx - 1]]


def diffspan(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, a[max(0, i - 12):len(a) - j + 12], b[max(0, i - 12):len(b) - j + 12]


if __name__ == "__main__":
    import sys
    for nnn in sys.argv[1:]:
        for s in parse_x7(nnn):
            c = current(s["chunk"], s["idx"])
            same = (c == s["tr"])
            print("\n=== %s  %s #%d  現行=材料:%s  材料%d字 現行%d字" %
                  (s["no"], s["chunk"], s["idx"], same, len(s["tr"]), len(c)))
            if not same:
                pos, x, y = diffspan(s["tr"], c)
                print("[差@%d] 材料…%s…" % (pos, x))
                print("        現行…%s…" % y)
