# -*- coding: utf-8 -*-
"""以「空行分段」為單位抽取 resp 876-925 的意見塊，分類並與現行 out 比對。"""
import re, os, json, glob

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
RESP = os.path.join(BASE, "batch_qwen", "r2")

paras = []
for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
    chunk = os.path.splitext(os.path.basename(p))[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            paras.append([chunk, idx, ln.strip()])

Q = re.compile(r"「([^」]{2,90})」")


def classify(b):
    if "✏" in b:
        return "A_潤飾"
    if re.search(r"加註|加注|註明|補註|出注|附註|補注|出註", b):
        return "B_加注"
    if re.search(r"潤飾|語感|生硬|不順|讀來|拗口|可再修|宜改|建議改|可作|宜作|改作", b):
        return "A_潤飾"
    if "⚠" in b:
        return "C_待商"
    if re.search(r"❌|❗", b):
        return "D_硬錯"
    if "💡" in b:
        return "B_加注"
    return "E_其他"


blocks = []
for n in range(876, 926):
    p = os.path.join(RESP, "resp_%d.txt" % n)
    if not os.path.exists(p):
        continue
    txt = open(p, encoding="utf-8").read()
    # 先切出段標，再切塊
    parts = re.split(r"\n\s*\n", txt)
    seg = ""
    for b in parts:
        b = b.strip()
        if not b:
            continue
        m = re.match(r"^#+\s*【?(\d{3}-\d{4})】?", b)
        if m and len(b) < 40:
            seg = m.group(1)
            continue
        m2 = re.search(r"【(\d{3}-\d{4})】", b)
        if m2:
            seg = m2.group(1)
        if b.startswith("#") and len(b) < 40:
            continue
        qs = [q.strip() for q in Q.findall(b)]
        hits = []
        for q in qs:
            q2 = q.strip(" ，。、；：")
            if len(q2) < 3:
                continue
            for chunk, idx, t in paras:
                if q2 in t:
                    # 判斷是否在該段的「」引文內
                    inq = ("「" + q2) in t or (q2 + "」") in t
                    hits.append({"q": q2, "chunk": chunk, "seg": idx, "inq": inq})
        blocks.append({"resp": n, "seg": seg, "kind": classify(b), "text": b, "hits": hits})

json.dump(blocks, open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps3_blocks.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

from collections import Counter
print(len(blocks), Counter(b["kind"] for b in blocks))
print("with hits:", sum(1 for b in blocks if b["hits"]))
print("with bare hits:", sum(1 for b in blocks if any(not h["inq"] for h in b["hits"])))
