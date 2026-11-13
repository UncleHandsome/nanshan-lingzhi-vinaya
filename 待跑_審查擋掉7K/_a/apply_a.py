# -*- coding: utf-8 -*-
"""套用 275/281/404 的判定改動（A組）。只換指定段落的問題處，其餘逐字不動。"""
import os, io, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K擋檔修正前")

# (chunk, 非空行序, [(find, new), ...])
EDITS = [
    ("01_行事鈔/08b_卷中之四", 32, [
        ("種種不同住人", "種種不共住人（受訶責等處分者）"),
        ("不欲令他們知曉而避走；在此處不名覆藏；若到了那處國土仍然覆藏",
         "因不欲讓他們知曉而未發露，在此處不名覆藏；但若到了他處國土仍然覆藏"),
    ]),
    ("01_行事鈔/08b_卷中之四", 33, [
        ("出罪則是一席大眾圓滿之法。",
         "出罪則無後續行法之期，僅是在二十位大眾集會中當席成辦之法（一席法）。"),
    ]),
    ("01_行事鈔/08c_卷中之四", 3, [
        ("修道者既然內心沒有守護戒律之心", "你身為修道人，既然內心沒有守護戒律之心"),
    ]),
    ("01_行事鈔/08c_卷中之四", 6, [
        ("但尚未達到究竟暢遂的人", "但犯罪尚未究竟遂行（未遂）者"),
        ("應當在結界外的四位比丘僧眾中懺悔", "應當出至結界之外，在四位比丘僧眾中懺悔"),
    ]),
    ("01_行事鈔/12a_卷下之四", 21, [
        ("三世身口意三業所造之一切罪障", "三世身口意三業的一切罪障"),
    ]),
]


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def main(dry=False):
    by_chunk = {}
    order = []
    for chunk, idx, ops in EDITS:
        by_chunk.setdefault(chunk, []).append((idx, ops))
        if chunk not in order:
            order.append(chunk)
    for chunk in order:
        book, name = chunk.split("/", 1)
        p = os.path.join(OUT, book, name + ".txt")
        raw = rd(p)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        for idx, ops in by_chunk[chunk]:
            i = idxs[idx - 1]
            old = lines[i]
            cur = old
            for find, new in ops:
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND 不唯一/不存在: %s#%d count=%d %r" % (chunk, idx, c, find))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("無變化: %s#%d" % (chunk, idx))
            lines[i] = cur
        if dry:
            print("[dry] %s  %d 段" % (chunk, len(by_chunk[chunk])))
            continue
        d = os.path.join(BAK, book)
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, name + "_a.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print("備份 %s" % os.path.relpath(bp, ROOT))
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：%d 段" % (chunk, len(by_chunk[chunk])))


if __name__ == "__main__":
    main(dry=("--dry" in sys.argv))
