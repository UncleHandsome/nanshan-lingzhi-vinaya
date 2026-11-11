# -*- coding: utf-8 -*-
"""潤飾覆核：套用 5 處修正（每次替換皆驗證唯一），並備份原檔。"""
import os, shutil, sys

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
BAK = os.path.join(BASE, "歸檔", "潤飾覆核前", "資持記")
os.makedirs(BAK, exist_ok=True)

EDITS = [
    ("01a_上一上.txt", 26, "教法詮定楷模標準", "教法所詮的楷式與決定",
     "「教詮楷定」譯作「教法詮定楷模標準」，主謂不接、語序破碎；「詮定」亦非成詞。"),
    ("01c_上一上.txt", 11, "的意思，意思是佛陀", "的意思，這是說佛陀",
     "「的意思，意思是」同語緊接重複。"),
    ("01c_上一上.txt", 24, "才構成罪犯", "才構成罪過",
     "「罪犯」為現代刑法語（犯罪之人），此處指構成過犯。"),
    ("02a_上一下.txt", 35, "其寬廣度也是普遍周全的", "其涵蓋的範圍也普遍周遍",
     "「寬廣度」非中文成詞（「-度」為現代構詞）；原文作「量亦普周」。"),
    ("02a_上一下.txt", 60, "善於統理率領廣大僧眾", "善於統御廣大僧眾",
     "「統理」「率領」同義連用，疊字冗贅；原文只作「善御大眾」。"),
]

files = {}
for fname, seg, old, new, why in EDITS:
    p = os.path.join(OUT, fname)
    if fname not in files:
        raw = open(p, "rb").read()
        assert b"\r\n" not in raw, fname + " has CRLF"
        assert raw[:3] != b"\xef\xbb\xbf", fname + " has BOM"
        files[fname] = raw.decode("utf-8")
        # 備份
        b = os.path.join(BAK, os.path.splitext(fname)[0] + "_p.txt")
        if not os.path.exists(b):
            shutil.copy2(p, b)
            print("backup:", b)

for fname, seg, old, new, why in EDITS:
    text = files[fname]
    lines = text.split("\n")
    idx = 0
    hit = -1
    for i, ln in enumerate(lines):
        if ln.strip():
            idx += 1
            if idx == seg:
                hit = i
                break
    assert hit >= 0, (fname, seg)
    assert lines[hit].count(old) == 1, (fname, seg, old, lines[hit].count(old))
    lines[hit] = lines[hit].replace(old, new, 1)
    files[fname] = "\n".join(lines)
    print("edit: %s#%d  %s -> %s" % (fname, seg, old, new))

for fname, text in files.items():
    p = os.path.join(OUT, fname)
    open(p, "w", encoding="utf-8", newline="\n").write(text)
    print("written:", p)
