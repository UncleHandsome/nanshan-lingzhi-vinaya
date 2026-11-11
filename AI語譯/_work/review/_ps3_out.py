# -*- coding: utf-8 -*-
"""輸出 A/B 類（潤飾、加注）且引文仍以「非引文」形式存在於現行段的意見塊。"""
import re, os, json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
blocks = json.load(open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps3_blocks.json"), encoding="utf-8"))

sel = []
for b in blocks:
    if b["kind"] not in ("A_潤飾", "B_加注"):
        continue
    bare = [h for h in b["hits"] if not h["inq"]]
    if not bare:
        continue
    locs = sorted({(h["chunk"], h["seg"]) for h in bare})
    # 只保留資持記檔案位置
    txt = re.sub(r"\s+", " ", b["text"])
    sel.append((b["resp"], b["seg"], b["kind"], "; ".join("%s#%d" % (c.split("_")[0], i) for c, i in locs), txt))

sel.sort()
lines = []
cur = None
for resp, seg, kind, loc, txt in sel:
    if resp != cur:
        cur = resp
        lines.append("\n===== resp_%d =====" % cur)
    lines.append("%s %s | %s" % (kind[0], seg or "-", txt))
out = "\n".join(lines)
open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps3_ab.txt"), "w", encoding="utf-8").write(out)
print("selected:", len(sel), "chars:", len(out))
