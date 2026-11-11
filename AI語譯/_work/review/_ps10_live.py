# -*- coding: utf-8 -*-
"""對每個 A 類意見塊，取其第一個引號詞（多為被批評的現譯片段），檢查是否仍存在於目標段。"""
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

Q = re.compile(r"「([^」]{2,90})」")
blocks = json.load(open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps3_blocks.json"), encoding="utf-8"))
rows = []
for b in blocks:
    if b["kind"] != "A_潤飾":
        continue
    qs = [q.strip(" ，。、；：") for q in Q.findall(b["text"])]
    if not qs:
        continue
    q0 = qs[0]
    if len(q0) < 3:
        continue
    tgt = None
    if b["seg"] in tag2seg and tag2seg[b["seg"]] in paras:
        tgt = tag2seg[b["seg"]]
    if tgt is None:
        for (ch, sg), t in paras.items():
            if q0 in t:
                tgt = (ch, sg)
                break
    if tgt is None:
        continue
    t = paras[tgt]
    if q0 not in t:
        continue  # 已改
    i = t.find(q0)
    s = max(0, i - 40); e = min(len(t), i + len(q0) + 40)
    rows.append("%s[%s#%d] 【%s】\n   %s\n" % (
        b["seg"] or "-", tgt[0].split("_")[0], tgt[1], q0, t[s:e]))

rows.sort()
open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps10_live.txt"), "w", encoding="utf-8").write("\n".join(rows))
print(len(rows), sum(len(r) for r in rows))
