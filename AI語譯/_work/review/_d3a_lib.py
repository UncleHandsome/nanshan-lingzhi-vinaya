# -*- coding: utf-8 -*-
"""7K 資持記 下三_a helpers."""
import os, re, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out", "資持記")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_d3a_view")


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def norm(t):
    return t.replace("\r\n", "\n").replace("\r", "\n")


def read_out(chunk):
    raw = read(os.path.join(OUT, chunk + ".txt"))
    eol = "\r\n" if "\r\n" in raw else ("\r" if "\r" in raw else "\n")
    lines = norm(raw).split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines, eol


def mat_map(n):
    t = norm(read(os.path.join(MAT, "校閱_%d.txt" % n)))
    items = []
    pat = re.compile(r"【(\d{4}-\d{4})】資持記/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【\d{4}-\d{4}】|\s*\Z)", re.S)
    for m in pat.finditer(t):
        items.append(dict(seg=m.group(1), chunk=m.group(2), idx=int(m.group(3)),
                          src=m.group(4).strip(), tr=m.group(5).strip()))
    return items


def view(n):
    os.makedirs(VIEW, exist_ok=True)
    buf = ["#" * 10 + " 意見 resp_%d " % n + "#" * 10]
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    buf.append(read(rp).strip() if os.path.exists(rp) else "(缺意見)")
    items = mat_map(n)
    buf.append("")
    buf.append("#" * 10 + " 段落 %d（%d 段）" % (n, len(items)) + "#" * 10)
    cache = {}
    for it in items:
        c = it["chunk"]
        if c not in cache:
            cache[c] = read_out(c)
        lines, eol = cache[c]
        ne = [(i, l) for i, l in enumerate(lines) if l.strip()]
        cur = ne[it["idx"] - 1][1].strip()
        same = cur == it["tr"]
        buf.append("\n--- %s  %s #%d  %s" % (it["seg"], c, it["idx"], "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + it["src"])
        buf.append("[譯文] " + cur)
        if not same:
            buf.append("[材料] " + it["tr"])
    p = os.path.join(VIEW, "v_%d.txt" % n)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print(p)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        view(int(a))
