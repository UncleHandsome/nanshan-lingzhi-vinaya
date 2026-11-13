# -*- coding: utf-8 -*-
"""列指定檔中「所引段未改」的意見區塊（截斷），供快速掃描。"""
import os, re, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    lines = rd(os.path.join(X7, "校閱_%s.txt" % nnn)).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "tr": ""}
            segs.append(cur)
            continue
        if cur is not None and ln.startswith("【譯文】"):
            cur["tr"] = ln[4:].strip()
    return segs


cache = {}
for n in [int(x) for x in sys.argv[1:]]:
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    if not os.path.exists(rp):
        continue
    txt = rd(rp).replace("\r\n", "\n")
    segs = parse_x7(n)
    st = {}
    for s in segs:
        if s["chunk"] not in cache:
            book, name = s["chunk"].split("/", 1)
            raw = rd(os.path.join(OUT, book, name + ".txt"))
            eol = "\r\n" if "\r\n" in raw else "\n"
            lines = raw.split(eol)
            cache[s["chunk"]] = (lines, [i for i, l in enumerate(lines) if l.strip()])
        lines, idxs = cache[s["chunk"]]
        cur = lines[idxs[s["idx"] - 1]].strip()
        st[s["no"]] = cur != s["tr"]
    print("\n" + "=" * 12, n, "=" * 12)
    for para in re.split(r"\n\s*\n", txt):
        p = para.strip()
        refs = sorted(set(re.findall(r"(\d{3,4}-\d{4})", p)))
        if not refs:
            continue
        if any(st.get(r) for r in refs):
            continue
        s = re.sub(r"\s+", " ", p)
        print("[%s] %s" % (",".join(refs), s[:260]))
