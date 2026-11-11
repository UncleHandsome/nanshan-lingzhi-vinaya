# -*- coding: utf-8 -*-
"""以備份還原受影響檔案（供修正後重新套用）。"""
import os, glob, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '現代詞修正前')

n = 0
for bk in sorted(os.listdir(BAK)):
    d = os.path.join(BAK, bk)
    if not os.path.isdir(d):
        continue
    for f in sorted(glob.glob(os.path.join(d, '*_m.txt'))):
        stem = os.path.basename(f)[:-len('_m.txt')]
        p = os.path.join(OUT, bk, stem + '.txt')
        shutil.copyfile(f, p)
        n += 1
print('還原', n, '檔')
