# -*- coding: utf-8 -*-
"""潤飾覆核：從 resp 876-921 抽出建議單元，與現行 out 段落比對，濾出「引文仍存在」者。"""
import re, os, json, glob

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
RESP = os.path.join(BASE, "batch_qwen", "r2")

def load_paras():
    paras = []  # (chunk, idx, text)
    for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
        chunk = os.path.splitext(os.path.basename(p))[0]
        lines = open(p, encoding="utf-8").read().split("\n")
        idx = 0
        for ln in lines:
            if ln.strip():
                idx += 1
                paras.append([chunk, idx, ln.strip()])
    return paras

paras = load_paras()
print("paragraphs:", len(paras))

Q = re.compile(r"「([^」]{2,80})」")

rows = []
for n in list(range(876, 926)):
    p = os.path.join(RESP, "resp_%d.txt" % n)
    if not os.path.exists(p):
        continue
    txt = open(p, encoding="utf-8").read()
    lines = txt.split("\n")
    seg = ""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"^#+\s*【?(\d{3}-\d{4})】?", s)
        if m:
            seg = m.group(1)
            continue
        if s.startswith("#"):
            continue
        # 建議單元：表格列 / 項目符號 / 含記號 / 含引文
        is_item = (s.startswith("|") or s.startswith("- ") or s.startswith("* ")
                   or re.search(r"[✏⚠❗❌💡★△○✅]", s) or Q.search(s))
        if not is_item:
            continue
        if s.startswith("|---") or set(s) <= set("|-: "):
            continue
        qs = [q for q in Q.findall(s)]
        if not qs:
            continue
        hits = []
        for q in qs:
            q2 = q.strip(" ，。、；：")
            if len(q2) < 4:
                continue
            for chunk, idx, t in paras:
                if q2 in t:
                    hits.append((q2, chunk, idx))
        rows.append({"resp": n, "seg": seg, "line": s, "quotes": qs,
                     "hits": hits})

json.dump(rows, open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps1_rows.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

withhit = [r for r in rows if r["hits"]]
print("items:", len(rows), "with hits:", len(withhit))

# 依 resp 分組輸出精簡清單（只列有命中者）
out = []
cur = None
for r in withhit:
    if r["resp"] != cur:
        cur = r["resp"]
        out.append("\n===== resp_%d =====" % cur)
    locs = sorted({(c, i) for (_, c, i) in r["hits"]})
    loc = " ".join("%s#%d" % (c.split("_")[0], i) for c, i in locs)
    out.append("[%s|%s] %s" % (r["seg"], loc, r["line"]))
open(os.path.join(BASE, "AI語譯", "_work", "review", "_ps1_view.txt"), "w", encoding="utf-8").write("\n".join(out))
print("view chars:", sum(len(x) for x in out))
