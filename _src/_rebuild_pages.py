# -*- coding: utf-8 -*-
"""暫存：線性驗證頁面差異只有插入標點（《 。），並原子替換。"""
import io
import os
import shutil
import subprocess
import sys
import time
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = ['xingshichao', 'yeshu', 'nicao', 'yichao']
VOLS = {'xingshichao': ['卷上', '卷中', '卷下'],
        'yeshu': ['卷一', '卷二', '卷三', '卷四'],
        'nicao': ['卷上', '卷中', '卷下'],
        'yichao': ['卷上', '卷中']}


def insert_only(old, new):
    """new 是否為 old 只插入字元；回傳 (ok, inserted_counter, first_bad)。"""
    i = j = 0
    ins = []
    n, m = len(old), len(new)
    while i < n or j < m:
        if i < n and j < m and old[i] == new[j]:
            i += 1
            j += 1
            continue
        if j < m and new[j] in '《「『（。':
            ins.append(new[j])
            j += 1
            continue
        return False, Counter(ins), (i, j, repr(old[i:i + 30]), repr(new[j:j + 30]))
    return True, Counter(ins), None


def main():
    apply = '--apply' in sys.argv
    bakdir = ''
    if apply:
        stamp = time.strftime('%Y%m%d_%H%M%S')
        bakdir = os.path.join(B, 'docs', '_備份_punctboundary_%s' % stamp)
        os.makedirs(bakdir, exist_ok=True)
        for bk in BOOKS:
            shutil.copytree(os.path.join(B, 'docs', bk), os.path.join(bakdir, bk))
        print('backup ->', bakdir)
    ok_all = True
    for bk in BOOKS:
        r = subprocess.run([sys.executable, '-X', 'utf8',
                            os.path.join(B, '_src', 'render_canonical_cb.py'), '--book', bk],
                           capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            print('RENDER FAIL', bk, r.stderr[-600:])
            ok_all = False
            continue
        for v in VOLS[bk]:
            p = os.path.join(B, 'docs', bk, v + '.html')
            q = p + '.new'
            old = io.open(p, encoding='utf-8').read()
            new = io.open(q, encoding='utf-8').read()
            ok, ins, bad = insert_only(old, new)
            print('%-12s %-4s old=%-7d new=%-7d insert=%-4d %s %s'
                  % (bk, v, len(old), len(new), sum(ins.values()), dict(ins),
                     '' if ok else ('BAD ' + repr(bad))))
            if not ok:
                ok_all = False
            if ok and apply:
                os.replace(q, p)
            elif os.path.exists(q):
                os.remove(q)
    print('ALL-INSERT-ONLY', ok_all, 'applied', apply)
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
