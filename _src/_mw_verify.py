# -*- coding: utf-8 -*-
"""驗證：逐行比對備份與現行，確認只動了預期的行，且行尾不變。"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _mw_edits import EDITS

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '現代詞修正前')

by_file = {}
for bk, stem, old, new, word in EDITS:
    by_file.setdefault((bk, stem), []).append((old, new, word))

bad = 0
tot_changed_lines = 0
for (bk, stem), items in sorted(by_file.items()):
    p = os.path.join(OUT, bk, stem + '.txt')
    q = os.path.join(BAK, bk, stem + '_m.txt')
    rb, rc = open(q, 'rb').read(), open(p, 'rb').read()
    if rb.count(b'\r\n') != rc.count(b'\r\n') or rb.count(b'\n') != rc.count(b'\n'):
        print('!! 行尾數變動', bk, stem)
        bad += 1
    tb, tc = rb.decode('utf-8'), rc.decode('utf-8')
    if len(tb) - len(tc) != sum(len(o) - len(n) for o, n, w in items) - (
            1 if (bk, stem) == ('01_行事鈔', '09a_卷下之一') else 0) * (len('審核')):
        # 允許 09a 一筆涵蓋兩處的長度差
        pass
    lb = re.split(r'\r?\n', tb)
    lc = re.split(r'\r?\n', tc)
    if len(lb) != len(lc):
        print('!! 行數變動', bk, stem, len(lb), len(lc))
        bad += 1
        continue
    for i, (a, b) in enumerate(zip(lb, lc)):
        if a == b:
            continue
        tot_changed_lines += 1
        # 檢查差異是否可完全由本檔的 edits 解釋
        exp = a
        for o, n, w in items:
            exp = exp.replace(o, n)
        if exp != b:
            print('!! 非預期變更 %s/%s 第%d行' % (bk, stem, i + 1))
            print('   原:', a[:120])
            print('   現:', b[:120])
            bad += 1

print('變更行數', tot_changed_lines, '筆數', len(EDITS), '異常', bad)
