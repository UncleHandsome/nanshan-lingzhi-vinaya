# -*- coding: utf-8 -*-
import json, io, os

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
jf = os.path.join(base, "AI語譯", "_work", "align_fix2", "001.json")
zf = os.path.join(base, "TXT", "資持記", "16_下四.txt")
cf = os.path.join(base, "TXT", "01_四分律刪繁補闕行事鈔.txt")
out = os.path.join(base, "AI語譯", "_work", "align_fix2", "_probe1.txt")

with io.open(jf, "r", encoding="utf-8") as f:
    data = json.load(f)
items = data["items"]
cand = data["cand"]

lines = io.open(zf, "r", encoding="utf-8").read().split("\n")
txt = "".join(l.strip() for l in lines[7:245])

pos = []
cur = 0
for it in items:
    t = it["text"]
    if it["z"] == 0:
        t = "題中四字"
    k = -1
    for L in (30, 24, 20, 16, 12, 8):
        k = txt.find(t[:L], cur)
        if k >= 0:
            break
    if k < 0:
        pos.append(None)
    else:
        pos.append(k)
        cur = k + 1

clines = io.open(cf, "r", encoding="utf-8").read().split("\n")
cao = {}
for idx in range(1560, 1574):  # lines 1560..1573 (1-based)
    cao[idx-1560] = clines[idx-1].strip()

w = io.open(out, "w", encoding="utf-8")
w.write("items %d cand %d\n" % (len(items), len(cand)))
w.write("positions: %s\n\n" % pos)

w.write("########## CAO PARAGRAPHS ##########\n")
for k in sorted(cao):
    w.write("[c%d] %s\n\n" % (k, cao[k]))

w.write("\n########## JI SEGMENTS ##########\n")
for i, it in enumerate(items):
    a = pos[i]
    b = pos[i+1] if i+1 < len(pos) and pos[i+1] is not None else len(txt)
    s = txt[a:b] if a is not None else ""
    w.write("===== z%d  len=%d  range=%s-%s =====\n" % (it["z"], len(s), a, b))
    w.write(s + "\n\n")
w.close()
print("ok")
