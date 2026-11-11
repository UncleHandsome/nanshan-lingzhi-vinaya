# -*- coding: utf-8 -*-
"""Emit markdown body of changed items grouped by category."""
import io, os, json, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
BAK = os.path.join(ROOT, "歸檔", "潤飾覆核前", "02_戒疏")

ops = json.load(io.open(os.path.join(HERE, "ops.json"), encoding="utf-8"))
rows = json.load(io.open(os.path.join(HERE, "final_rows.json"), encoding="utf-8"))
segof = {(r["chunk"][:3], r["seg"]): r["cat"] for r in rows}

# locate each op in backups
backs = {}
for f in os.listdir(BAK):
    if f.endswith("_p.txt"):
        ch = f[:-6]
        raw = io.open(os.path.join(BAK, f), encoding="utf-8", newline="").read()
        sep = "\r\n\r\n" if "\r\n" in raw else "\n\n"
        backs[ch] = raw.split(sep)

def loc(q):
    out = []
    for ch, ps in backs.items():
        for i, p in enumerate(ps):
            if q in p:
                out.append((ch, i + 1))
    return out

CAT = {"1": "讀不通", "2": "生造詞", "3": "現代詞誤用", "4": "重複贅字"}
items = collections.defaultdict(list)
SKIP = {"12b 認領三"}
for op in ops:
    if op.get("tag") in SKIP:
        continue
    for ch, seg in loc(op["q"]):
        items[op["cat"]].append((ch[:3], seg, op["q"], op["new"]))
# extras
extras = [("14c", 142, "【律文】如果比丘，進行種種買賣交易的。", "【律文】若比丘從事種種買賣交易者。", "1"),
          ("12b", 37, "如果是未達規定尺寸以內的碎料", "如果是不及規定尺寸的碎料", "1"),
          ("10b", 43, "（突吉羅）（突吉羅）", "（突吉羅）", "4")]
for ch, seg, q, new, c in extras:
    items[c].append((ch, seg, q, new))

for c in "1234":
    lst = sorted(set(items[c]))
    print("### %s（%d 段／%d 處）" % (CAT[c], len({(a, b) for a, b, _, _ in lst}), len(lst)))
    print()
    print("| 段 | 原 | 改 |")
    print("|---|---|---|")
    for ch, seg, q, new in lst:
        print("| %s#%d | %s | %s |" % (ch, seg, q.replace("|", "／")[:46], new.replace("|", "／")[:46]))
    print()
