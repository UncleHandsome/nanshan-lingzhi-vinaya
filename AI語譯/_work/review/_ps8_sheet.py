# -*- coding: utf-8 -*-
"""為每個 A 類意見塊定位目標段，輸出「意見 + 現行段該處上下文」對照表。"""
import re, os, glob, json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
COV = ("01a", "01b", "01c", "01d", "01e", "01f", "02a")

paras = {}
for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
    base = os.path.basename(p)
    if not any(base.startswith(f) for f in COV):
        continue
    chunk = os.path.splitext(base)[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            paras[(chunk, idx)] = ln.strip()

tag2seg = {}
for p in glob.glob(os.path.join(BASE, "校閱_10K", "校閱_*.txt")):
    for ln in open(p, encoding="utf-8"):
        m = re.match(r"^【(\d{3}-\d{4})】\s*資持記/(\S+)#(\d+)\s*$", ln.strip())
        if m:
            tag2seg[m.group(1)] = (m.group(2), int(m.group(3)))

blocks = json.load(open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps3_blocks.json"), encoding="utf-8"))
out = []
for b in blocks:
    if b["kind"] != "A_潤飾":
        continue
    bare = [h for h in b["hits"] if not h["inq"] and (h["chunk"], h["seg"]) in paras]
    if not bare:
        continue
    # 目標段
    target = None
    if b["seg"] in tag2seg:
        t = tag2seg[b["seg"]]
        if t in paras:
            target = t
    if target is None:
        target = (bare[0]["chunk"], bare[0]["seg"])
    t = paras[target]
    q = bare[0]["q"]
    i = t.find(q)
    if i < 0:
        i = 0
    s = max(0, i - 45); e = min(len(t), i + len(q) + 45)
    txt = re.sub(r"\s+", " ", b["text"])[:260]
    out.append("%s[%s] 意見: %s\n    現文: …%s…\n" % (
        b["seg"] or "-", "%s#%d" % (target[0].split("_")[0], target[1]), txt, t[s:e]))
open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps8_sheet.txt"), "w", encoding="utf-8").write("\n".join(out))
print(len(out), sum(len(x) for x in out))
