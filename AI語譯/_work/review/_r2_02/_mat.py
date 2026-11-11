# -*- coding: utf-8 -*-
"""Show material blocks (原文+譯文) and current paragraph for given resp/seg pairs.

Usage: python _mat.py 647:112,643:30 [--full]
"""
import io, os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
J10 = os.path.join(ROOT, "校閱_10K")
PER = json.load(io.open(os.path.join(HERE, "tmp_per.json"), encoding="utf-8"))


def seg_paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps


def main(arg, full=False):
    L = []
    for pair in arg.split(","):
        d = None
        if ":" in pair:
            n, s = pair.split(":")
            n = int(n); s = int(s)
            d = PER[str(n)]
            chunk = None
            for k, v in d.items():
                if v[1] == s:
                    chunk = v[0].split("/")[1]
                    break
        else:
            key = pair.split("-")[0].lstrip("0") if False else pair
            k3, k4 = pair.split("-")
            n = int(k3); key = k3.zfill(3) + "-" + k4
            d = PER[str(n)]
            chunk = d[key][0].split("/")[1]
            s = d[key][1]
        t = io.open(os.path.join(J10, "校閱_%03d.txt" % n), encoding="utf-8-sig", errors="replace").read()
        # split material into blocks by 【id】
        parts = re.split(r"(?=【\d{3}-\d{4}】)", t)
        blk = None
        for p in parts:
            mm = re.match(r"【(\d{3})-(\d{4})】\s*([^#\r\n]+?)#(\d+)", p)
            if mm and mm.group(1) == str(n) and int(mm.group(4)) == s:
                blk = p
                break
        L.append("=" * 20 + " %d:%d  chunk=%s" % (n, s, chunk))
        if blk:
            L.append(blk.strip())
        else:
            L.append("(material block not found)")
        if chunk:
            ps = seg_paras(chunk)
            L.append("-- NOW #%d --" % s)
            L.append(ps[s - 1] if 0 < s <= len(ps) else "NA")
        L.append("")
    out = "\n".join(L)
    p = os.path.join(HERE, "_mat_out.txt")
    io.open(p, "w", encoding="utf-8").write(out)
    print(p, len(out))


if __name__ == "__main__":
    main(sys.argv[1], "--full" in sys.argv)
