# -*- coding: utf-8 -*-
"""Verify c-pass: for edited chunks compare current file with pre-pass backup (_c)."""
import io, os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
ARCH = os.path.join(ROOT, "歸檔", "r2修正前", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")


def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()


def split(t):
    sep = "\r\n\r\n" if "\r\n\r\n" in t else "\n\n"
    ps = t.split(sep)
    if ps and ps[-1] == "":
        ps = ps[:-1]
    return ps, sep


def main(toks):
    log = {}
    for line in io.open(os.path.join(HERE, "_c_log.jsonl"), encoding="utf-8"):
        j = json.loads(line)
        log.setdefault(j["chunk"], set()).add(j["seg"])
    bad = 0
    for tok in toks:
        names = [n for n in os.listdir(OUTD) if n.startswith(tok + "_") and n.endswith(".txt")]
        if not names:
            print("NOFILE", tok); bad += 1; continue
        name = names[0]
        chunk = name[:-4]
        cur = rd(os.path.join(OUTD, name))
        bpath = os.path.join(ARCH, chunk + "_c.txt")
        if not os.path.exists(bpath):
            print("NOBACKUP", chunk); bad += 1; continue
        old = rd(bpath)
        pc, sep = split(cur)
        po, sepo = split(old)
        crlf = cur.count("\r\n")
        lf = cur.count("\n")
        diff = [i + 1 for i, (a, b) in enumerate(zip(pc, po)) if a != b]
        exp = sorted(log.get(chunk, []))
        ok = (len(pc) == len(po) and sep == sepo and crlf == lf and diff == exp)
        print("%-22s paras %d/%d sep %s crlf=%d/lf=%d diff=%d exp=%d %s" % (
            chunk, len(pc), len(po), "CRLF" if sepo.strip() else "??", crlf, lf,
            len(diff), len(exp), "OK" if ok else "MISMATCH"))
        if not ok:
            print("   diff segs:", diff)
            print("   expected :", exp)
            bad += 1
    print("ALL OK" if bad == 0 else "BAD %d" % bad)


if __name__ == "__main__":
    main(sys.argv[1:])
