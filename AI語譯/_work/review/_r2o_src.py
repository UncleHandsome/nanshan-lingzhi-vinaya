# -*- coding: utf-8 -*-
"""Index: (book, chunk, seg) -> 原文, built from 校閱_10K materials 1393-1912."""
import io, os, re, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
BOOKS = ("03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔")

def main():
    idx = {}
    for fn in sorted(os.listdir(MAT)):
        if not fn.startswith("校閱_"):
            continue
        n = int(re.sub(r"\D", "", fn))
        if n < 1393:
            continue
        t = io.open(os.path.join(MAT, fn), encoding="utf-8").read()
        blocks = re.split(r"(?=【\d{4}-\d{4}】)", t)
        for b in blocks:
            m = re.match(r"【(\d{4}-\d{4})】([^\r\n/]+)/([^#\r\n]+)#(\d+)", b)
            if not m:
                continue
            book = m.group(2).strip()
            if book not in BOOKS:
                continue
            chunk = m.group(3).strip()
            seg = int(m.group(4))
            src = ""
            ms = re.search(r"【原文】(.*?)(?=\n【譯文】|\n*$)", b, re.S)
            if ms:
                src = ms.group(1).strip()
            idx.setdefault(book, {}).setdefault(chunk, {})[str(seg)] = src
    json.dump(idx, io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2o_src.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    tot = sum(len(v) for b in idx.values() for v in b.values())
    print("books:", list(idx))
    for bk in idx:
        print(" ", bk, "chunks", len(idx[bk]), "segs", sum(len(v) for v in idx[bk].values()))
    print("total segs:", tot)

if __name__ == "__main__":
    main()
