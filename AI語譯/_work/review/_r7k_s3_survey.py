# -*- coding: utf-8 -*-
"""資持記 上三（檔 1458-1503）7K 校閱：材料盤點 + 檢視。"""
import os, sys, re, json, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_s3_view")

N0, N1 = 1458, 1503


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
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)),
                   "src": "", "tr": ""}
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
    return i, a[max(0, i - 12):len(a) - j + 12], b[max(0, i - 12):len(b) - j + 12]


def survey():
    rows = []
    for n in range(N0, N1 + 1):
        segs = parse_x7(n)
        same = 0
        for s in segs:
            raw, eol, lines, idxs, p = read_chunk(s["chunk"])
            c = lines[idxs[s["idx"] - 1]].strip()
            s["cur"] = c
            s["same"] = (c == s["tr"])
            if s["same"]:
                same += 1
        rp = os.path.join(RESP, "resp_%d.txt" % n)
        rows.append({"no": n, "segs": len(segs), "same": same,
                     "chunks": sorted({s["chunk"] for s in segs}),
                     "resp": os.path.exists(rp),
                     "resp_len": len(rd(rp)) if os.path.exists(rp) else 0})
    print("檔\t段數\t同材料\tchunks\t意見")
    for r in rows:
        print("%d\t%d\t%d\t%s\t%s" % (r["no"], r["segs"], r["same"],
                                      ",".join(r["chunks"]), r["resp_len"]))
    print("\n總段數 %d，同材料 %d" % (sum(r["segs"] for r in rows), sum(r["same"] for r in rows)))
    print("意見缺檔:", [r["no"] for r in rows if not r["resp"]])


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("=" * 24 + " 意見 resp_%s " % nnn + "=" * 24)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("=" * 24 + " 段落 %s（%d 段）" % (nnn, len(segs)) + "=" * 24)
    for s in segs:
        raw, eol, lines, idxs, p = read_chunk(s["chunk"])
        c = lines[idxs[s["idx"] - 1]].strip()
        same = (c == s["tr"])
        buf.append("\n--- %s  #%d  %s" % (s["no"], s["idx"],
                                          "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[材料譯文] " + s["tr"])
        if not same:
            pos, x, y = diffspan(s["tr"], c)
            buf.append("[現行譯文] " + c)
            buf.append("[差異@%d] 材料…%s… / 現行…%s…" % (pos, x, y))
    out = os.path.join(VIEW, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "survey":
        survey()
    elif cmd == "show":
        for n in sys.argv[2:]:
            show(n)
