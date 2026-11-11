# -*- coding: utf-8 -*-
"""細分：把候選分成「潤飾型(✏️/💡/加注)」與「其他」，並標示引文在現行段中的位置型態。"""
import re, os, json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
rows = json.load(open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps1_rows.json"), encoding="utf-8"))

def kind(s):
    if "✏" in s:
        return "A_潤飾"
    if "💡" in s:
        return "B_加注"
    if re.search(r"加註|加注|註明|補註|出注|附註", s):
        return "B_加注"
    if re.search(r"潤飾|語感|生硬|不順|讀來|順暢|可再修|可改作|宜改|建議改", s):
        return "A_潤飾"
    if "⚠" in s:
        return "C_待商"
    if re.search(r"❌|❗", s):
        return "D_硬錯"
    return "E_其他"

buckets = {}
for r in rows:
    if not r["hits"]:
        continue
    k = kind(r["line"])
    buckets.setdefault(k, []).append(r)
for k in sorted(buckets):
    print(k, len(buckets[k]))

# 輸出 A+B 類，按 resp 排序，附段位置
sel = [(k, r) for k in ("A_潤飾", "B_加注") for r in buckets.get(k, [])]
sel.sort(key=lambda kr: (kr[1]["resp"], kr[1]["seg"]))
out = []
cur = None
for k, r in sel:
    if r["resp"] != cur:
        cur = r["resp"]
        out.append("\n===== resp_%d =====" % cur)
    locs = sorted({(c, i) for (_, c, i) in r["hits"]})
    loc = " ".join("%s#%d" % (c.split("_")[0], i) for c, i in locs)
    out.append("%s [%s|%s] %s" % (k[0], r["seg"], loc, r["line"]))
txt = "\n".join(out)
open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps1_ab.txt"), "w", encoding="utf-8").write(txt)
print("A+B items:", len(sel), "chars:", len(txt))
