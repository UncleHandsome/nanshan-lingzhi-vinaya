# -*- coding: utf-8 -*-
"""複審套用：json = [{"no":"515-0002","find":"..","new":".."}, ...]
以 校閱_NNN.txt 定位段→(chunk, idx)，就地替換該行，保持 EOL 與段數。"""
import os, re, io, json, sys, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = {}, None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = (m.group(2), int(m.group(3)))
            segs[m.group(1)] = cur
    return segs


def main(jf, dry):
    items = json.loads(rd(jf))
    by_chunk = {}
    for it in items:
        c = it["no"].split("-")[0]
        by_chunk.setdefault(c, []).append(it)
    for c, its in sorted(by_chunk.items()):
        segs = parse_x7(c)
        chunks = sorted({v[0] for v in segs.values()})
        assert len(chunks) == 1, chunks
        chunk = chunks[0]
        book, name = chunk.split("/", 1)
        p = os.path.join(OUT, book, name + ".txt")
        raw = rd(p)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        nedit = 0
        for it in its:
            ch, idx = segs[it["no"]]
            i = idxs[idx - 1]
            cur = lines[i]
            n = cur.count(it["find"])
            if n != 1:
                raise SystemExit("FIND count=%d %s: %r" % (n, it["no"], it["find"]))
            lines[i] = cur.replace(it["find"], it["new"])
            nedit += 1
        print("%s %s: %d 處" % (c, chunk, nedit))
        if not dry:
            with io.open(p, "w", encoding="utf-8", newline="") as f:
                f.write(eol.join(lines))
    print("done", "dry" if dry else "written")


if __name__ == "__main__":
    main(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "dry")
