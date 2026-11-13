# -*- coding: utf-8 -*-
"""複審用精簡視圖：只印 resp 中出現的段，及該段原文/材料/現行(僅異動時)。"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view")


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


def read_chunk(chunk):
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return lines, idxs


def main(nnn):
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf = ["#" * 10 + " 意見 resp_%s " % nnn + "#" * 10]
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺)")
    segs = parse_x7(nnn)
    buf.append("\n" + "#" * 10 + " 段落 %s（%d 段）" % (nnn, len(segs)) + "#" * 10)
    cur_chunk = None
    lines = idxs = None
    for s in segs:
        if s["chunk"] != cur_chunk:
            cur_chunk = s["chunk"]
            lines, idxs = read_chunk(cur_chunk)
            buf.append("\n@@ chunk=%s 非空行=%d" % (cur_chunk, len(idxs)))
        c = lines[idxs[s["idx"] - 1]].strip()
        same = (c == s["tr"])
        buf.append("\n-- %s #%d %s" % (s["no"], s["idx"], "現行=材料" if same else "※異動"))
        buf.append("[原] " + s["src"])
        if same:
            buf.append("[文] " + s["tr"])
        else:
            buf.append("[材] " + s["tr"])
            buf.append("[現] " + c)
    out = os.path.join(VIEW, "fx_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
