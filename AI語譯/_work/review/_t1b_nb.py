# -*- coding: utf-8 -*-
import os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
out = os.path.join(base, "AI語譯", "out")
work = os.path.join(base, "AI語譯", "_work", "review", "_t1b_ctx")
os.makedirs(work, exist_ok=True)

def paras(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

rows = [
    ("03_業疏", "04a_卷一之四", 95, 3),
    ("03_業疏", "13a_卷三之二", 61, 3),
    ("02_戒疏", "14a_卷三下之二", 9, 2),
    ("02_戒疏", "14b_卷三下之二", 21, 3),
    ("02_戒疏", "14b_卷三下之二", 79, 3),
    ("02_戒疏", "14b_卷三下之二", 87, 3),
    ("02_戒疏", "14b_卷三下之二", 102, 3),
    ("02_戒疏", "14b_卷三下之二", 171, 3),
    ("02_戒疏", "10c_卷三上之一", 76, 3),
    ("04_比丘尼鈔", "01b_卷上之上", 85, 1),
]
for book, chunk, seg, span in rows:
    o = paras(os.path.join(out, book, chunk + ".txt"))
    i = seg - 1
    buf = [f"### {book} {chunk} seg={seg} out_paras={len(o)}"]
    for j in range(max(0, i - span), min(len(o), i + span + 1)):
        mark = ">>>" if j == i else "   "
        buf.append(f"{mark} out[{j+1}]: {o[j]}")
    with open(os.path.join(work, f"_nb_{book}_{chunk}_{seg}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(buf) + "\n")
print("ok")
