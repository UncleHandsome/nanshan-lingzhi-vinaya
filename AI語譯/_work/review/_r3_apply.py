# -*- coding: utf-8 -*-
"""ret3 套用：備份（<chunk>_ret3_v.txt）後套用 _r3_edits.json，並印出報告。"""
import io
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r3_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
BAK = os.path.join(L.ROOT, "歸檔", "7K卷修正前")

dat = json.load(io.open(os.path.join(HERE, "_r3_edits.json"), encoding="utf-8"))

# 1) 備份
made = []
for book, chunk in sorted(set((e["book"], e["chunk"]) for e in dat)):
    d = os.path.join(BAK, L.BOOKDIR[book])
    os.makedirs(d, exist_ok=True)
    src = L.path(book, chunk)
    dst = os.path.join(d, chunk + "_ret3_v.txt")
    if os.path.exists(dst):
        print("備份已存在，略過：", dst)
    else:
        shutil.copy2(src, dst)
        made.append(dst)
print("新備份 %d 檔：" % len(made))
for m in made:
    print("  ", m)

# 2) 套用
print()
print("== 套用 ==")
for r in L.apply(dat):
    print("  ", r)
