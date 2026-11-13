# -*- coding: utf-8 -*-
"""記文小窗檢索：只印命中處前後 N 字，避免整行。"""
import io, re, sys

P = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\TXT\02_四分律含注戒本疏.txt"
txt = io.open(P, encoding="utf-8").read().replace("\r\n", "\n")
buf = []
for pat in sys.argv[1:]:
    buf.append("=== %s" % pat)
    for m in re.finditer(pat, txt):
        a, b = max(0, m.start() - 80), min(len(txt), m.end() + 80)
        s = txt[a:b].replace("\n", "\\n")
        buf.append("  …%s…" % s)
out = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_r7k_view\grep_tmp.txt"
io.open(out, "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("wrote", out)
