# -*- coding: utf-8 -*-
"""Final stats: enumerate all changed paragraphs vs backup; assign categories from ops."""
import io, os, json, re, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
BAK = os.path.join(ROOT, "歸檔", "潤飾覆核前", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")

ops = json.load(io.open(os.path.join(HERE, "ops.json"), encoding="utf-8"))
extra = [("14c_卷三下之二", "【律文】如果比丘，進行種種買賣交易的。", "【律文】若比丘從事種種買賣交易者。", "1"),
         ("12b_卷三上之三", "如果是未達規定尺寸以內的碎料", "如果是不及規定尺寸的碎料", "1"),
         ("15d_卷三下之三", "過了期限也應該失去受日法嗎", "受了受日法卻還沒出界", "1"),
         ("10b_卷三上之一", "（突吉羅）（突吉羅）", "（突吉羅）", "4")]

rows = []
for f in sorted(os.listdir(BAK)):
    if not f.endswith("_p.txt"): continue
    ch = f[:-6]
    cur = io.open(os.path.join(OUTD, ch + ".txt"), encoding="utf-8", newline="").read()
    old = io.open(os.path.join(BAK, f), encoding="utf-8", newline="").read()
    sep = "\r\n\r\n" if "\r\n" in cur else "\n\n"
    a, b = old.split(sep), cur.split(sep)
    assert len(a) == len(b), ch
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y: continue
        cats = []
        for op in ops:
            if op["q"] in x and op["new"] in y:
                cats.append(op["cat"])
        for ech, eq, en, ec in extra:
            if ech == ch and eq in x and en in y:
                cats.append(ec)
        if not cats:
            cats.append("?")
        rows.append({"chunk": ch, "seg": i + 1, "cats": cats})

cnt = collections.Counter()
for r in rows:
    # priority: 1 unreadable > 2 coined > 3 modern > 4 redundancy
    for c in ["1", "2", "3", "4"]:
        if c in r["cats"]:
            r["cat"] = c
            break
    else:
        r["cat"] = "?"
    cnt[r["cat"]] += 1

print("changed paras", len(rows))
print("by cat", dict(sorted(cnt.items())))
print("chunks", len({r['chunk'] for r in rows}))
print("question", [r for r in rows if r["cat"] == "?"])
json.dump(rows, io.open(os.path.join(HERE, "final_rows.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
