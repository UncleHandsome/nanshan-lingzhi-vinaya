# -*- coding: utf-8 -*-
"""精簡視圖：只印意見中的硬錯提示 + 每段原文/譯文。用法: python _r7k_lean.py 1402 ..."""
import sys, os, io, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r7k_z02 as Z

KEYS = ("❌", "❗", "❶", "必改", "誤譯", "應作", "建議改", "硬傷", "錯誤")


def show_text(nnn):
    buf = []
    rp = os.path.join(Z.RESP, "resp_%s.txt" % nnn)
    if os.path.exists(rp):
        buf.append("### 意見硬點 %s" % nnn)
        for ln in Z.rd(rp).split("\n"):
            s = ln.strip()
            if not s or len(s) > 220:
                continue
            if any(k in s for k in KEYS):
                buf.append(s)
    else:
        buf.append("### 意見缺 %s" % nnn)
    segs = Z.parse_x7(nnn)
    for s in segs:
        raw, eol, lines, idxs, p = Z.read_chunk(s["chunk"])
        c = lines[idxs[s["idx"] - 1]].strip()
        same = (c == s["tr"])
        buf.append("\n--- %s #%d %s" % (s["no"], s["idx"], "現行=材料" if same else "※已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[譯文] " + c)
    return "\n".join(buf)


def show(nnn):
    print(show_text(nnn))


args = sys.argv[1:]
if args and args[0].startswith("--out="):
    out = args[0][6:]
    buf = []
    for a in args[1:]:
        buf.append(show_text(a))
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(buf))
    print("wrote " + out)
else:
    for a in args:
        show(a)
