# -*- coding: utf-8 -*-
"""ret3 套用後驗證：備份逐段比對，確認段數／行數／行尾不變且僅動預定段。"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r3_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
BAK = os.path.join(L.ROOT, "歸檔", "7K卷修正前")
dat = json.load(io.open(os.path.join(HERE, "_r3_edits.json"), encoding="utf-8"))

byfile = {}
for e in dat:
    byfile.setdefault((e["book"], e["chunk"]), set()).add(e["para"])

print("== 驗證 ==")
ok = True
for (book, chunk), want in sorted(byfile.items()):
    b = io.open(os.path.join(BAK, L.BOOKDIR[book], chunk + "_ret3_v.txt"), encoding="utf-8", newline="").read()
    a = io.open(L.path(book, chunk), encoding="utf-8", newline="").read()
    sb = L.sep(b)
    sa = L.sep(a)
    pb, pa = b.split(sb), a.split(sa)
    diff = [i + 1 for i in range(len(pb)) if pb[i] != pa[i]]
    same = (len(pb) == len(pa)) and (b.count("\n") == a.count("\n")) and (b.count("\r") == a.count("\r") == 0)
    good = same and sorted(diff) == sorted(want)
    ok = ok and good
    print("%s [%s %s] 段 %d->%d 行 %d->%d CR %d->%d 變動段 %s (預定 %s) 位元組 %d->%d"
          % ("OK " if good else "!! ", book, chunk,
             len(pb), len(pa), b.count("\n"), a.count("\n"), b.count("\r"), a.count("\r"),
             diff, sorted(want), len(b.encode("utf-8")), len(a.encode("utf-8"))))
print()
print("全部通過" if ok else "有異常")
