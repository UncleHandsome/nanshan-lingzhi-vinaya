# -*- coding: utf-8 -*-
"""資持記 上三 7K 校閱：套用修改。
用法: python _r7k_s3_apply.py edits_1458_1461.json
edits: {"資持記/04a_上三": {"1458-0001": {"idx":2, "ops":[["find","new"],...]}, ...}}
"""
import os, sys, re, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def apply(edits):
    total = 0
    for chunk, segs in edits.items():
        book, name = chunk.split("/", 1)
        p = os.path.join(OUT, book, name + ".txt")
        raw = rd(p)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        for no, e in segs.items():
            idx = e["idx"]
            i = idxs[idx - 1]
            old = lines[i]
            cur = old
            for find, new in e["ops"]:
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (no, idx, c, find))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("無變化: %s #%d" % (no, idx))
            lines[i] = cur
            total += 1
        d = os.path.join(BAK, book)
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, name + "_v.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print("備份 %s" % os.path.relpath(bp, ROOT))
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：%d 段" % (chunk, len(segs)))
    print("合計 %d 段" % total)


if __name__ == "__main__":
    for f in sys.argv[1:]:
        apply(json.loads(rd(f)))
