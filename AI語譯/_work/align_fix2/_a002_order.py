# -*- coding: utf-8 -*-
import io, json, os

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D = os.path.join(B, "AI語譯", "_work", "align_fix2")
data = json.load(io.open(os.path.join(D, "002.json"), encoding="utf-8"))
out = json.load(io.open(os.path.join(D, "out_002.json"), encoding="utf-8"))
items = {it["z"]: it["text"] for it in data["items"]}
cands = {c["c"]: c["text"] for c in data["cand"]}
mp = {m["z"]: m["c"] for m in out["map"]}

lines = []
for c in sorted(cands):
    lines.append("【鈔 %02d】%s" % (c, cands[c][:46]))
    for z in sorted(mp):
        if mp[z] == c:
            lines.append("      【記 z%02d】%s" % (z, items[z][:46]))
io.open(os.path.join(D, "_a002_order.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
