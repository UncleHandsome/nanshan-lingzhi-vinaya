# -*- coding: utf-8 -*-
"""套用現代詞修正：先檢查唯一性，再備份、改寫。"""
import io, os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _mw_edits import EDITS

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '現代詞修正前')
ALLOW_ALL = {('01_行事鈔', '09a_卷下之一', '雜項問題的審核辨析')}

dry = '--apply' not in sys.argv

# 1) 檢查
problems = []
by_file = {}
for bk, stem, old, new, word in EDITS:
    by_file.setdefault((bk, stem), []).append((old, new, word))

for (bk, stem), items in by_file.items():
    p = os.path.join(OUT, bk, stem + '.txt')
    t = open(p, 'rb').read().decode('utf-8')
    for old, new, word in items:
        n = t.count(old)
        keyflag = (bk, stem, old) in ALLOW_ALL
        if n == 0:
            problems.append('缺: %s/%s %s 「%s」' % (bk, stem, word, old))
        elif n > 1 and not keyflag:
            problems.append('重複%d: %s/%s %s 「%s」' % (n, bk, stem, word, old))
        if n >= 1 and old in new:
            # 只有新字串包含舊字串時，殘留次數才有意義
            if t.count(new) > t.count(old):
                problems.append('新字串已存在%d: %s/%s 「%s」' % (t.count(new), bk, stem, new))

if problems:
    print('== 檢查問題 ==')
    for x in problems:
        print(' ', x)
    if dry:
        print('（dry run 結束）')
        sys.exit(1)

if dry:
    print('檢查通過：%d 筆，%d 檔' % (len(EDITS), len(by_file)))
    sys.exit(0)

# 2) 備份 + 改寫
os.makedirs(os.path.join(BAK), exist_ok=True)
changed_files = 0
for (bk, stem), items in by_file.items():
    p = os.path.join(OUT, bk, stem + '.txt')
    raw = open(p, 'rb').read()
    t = raw.decode('utf-8')
    dst_dir = os.path.join(BAK, bk)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, stem + '_m.txt')
    if not os.path.exists(dst):
        shutil.copyfile(p, dst)
    for old, new, word in items:
        if (bk, stem, old) in ALLOW_ALL:
            t = t.replace(old, new)
        else:
            assert t.count(old) == 1, (bk, stem, old, t.count(old))
            t = t.replace(old, new)
    out = t.encode('utf-8')
    open(p, 'wb').write(out)
    changed_files += 1

print('已改 %d 檔、%d 筆' % (changed_files, len(EDITS)))
