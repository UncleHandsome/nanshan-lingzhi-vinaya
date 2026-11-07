# -*- coding: utf-8 -*-
import os, io

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
src = os.path.join(base, "TXT_分卷")
out = os.path.join(base, "AI語譯", "out")
work = os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx")
os.makedirs(work, exist_ok=True)

rows = [
    ("04_比丘尼鈔", "01b_卷上之上", 85),
    ("03_業疏", "04a_卷一之四", 95),
    ("03_業疏", "05b_卷一之五", 22),
    ("03_業疏", "13a_卷三之二", 61),
    ("02_戒疏", "14a_卷三下之二", 9),
    ("02_戒疏", "14b_卷三下之二", 21),
    ("02_戒疏", "14b_卷三下之二", 79),
    ("02_戒疏", "14b_卷三下之二", 87),
    ("02_戒疏", "14b_卷三下之二", 102),
    ("02_戒疏", "14b_卷三下之二", 171),
    ("02_戒疏", "10c_卷三上之一", 76),
]

def paras(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

for book, chunk, seg in rows:
    sp = os.path.join(src, book, chunk + ".txt")
    s = paras(sp)
    o = paras(os.path.join(out, book, chunk + ".txt"))
    i = seg - 1
    buf = [f"BOOK={book} CHUNK={chunk} SEG={seg} src_paras={len(s)} out_paras={len(o)}"]
    for j in range(max(0, i - 2), min(len(s), i + 3)):
        buf.append(f"--- src[{j+1}] ---\n{s[j]}")
    for j in range(max(0, i - 1), min(len(o), i + 2)):
        buf.append(f"--- out[{j+1}] ---\n{o[j]}")
    fn = f"{book}__{chunk}__{seg}.txt"
    with open(os.path.join(work, fn), "w", encoding="utf-8") as f:
        f.write("\n".join(buf) + "\n")
print("done")
