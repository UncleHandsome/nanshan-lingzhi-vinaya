# -*- coding: utf-8 -*-
"""列出 resp 各檔的意見條目（標題＋首段摘要），供分類掃描。"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
OUT = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_view")
SEG = re.compile(r"\d{3,4}-\d{4}")
HEAD = re.compile(r"^(#{2,4})\s*(.*)$")


def items(text):
    out, cur = [], None
    for ln in text.split("\n"):
        s = ln.rstrip()
        m = HEAD.match(s)
        if m and len(m.group(1)) >= 3:
            if cur:
                out.append(cur)
            cur = [s, []]
            continue
        if cur is not None:
            if s.strip():
                cur[1].append(s.strip())
    if cur:
        out.append(cur)
    return out


buf = []
for n in sys.argv[1:]:
    p = os.path.join(RESP, "resp_%s.txt" % n)
    if not os.path.exists(p):
        buf.append("### %s 缺" % n)
        continue
    t = io.open(p, encoding="utf-8").read()
    buf.append("\n######## %s ########" % n)
    for h, body in items(t):
        sn = SEG.findall(h)
        tag = sn[0] if sn else "----"
        b = " ".join(body)[:230]
        buf.append("[%s] %s || %s" % (tag, h.strip("# ").strip(), b))
open(os.path.join(OUT, "items_%s.txt" % sys.argv[1]), "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
print("ok %d" % len(buf))
