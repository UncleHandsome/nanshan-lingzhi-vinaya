# -*- coding: utf-8 -*-
"""從備份 diff 計算真實統計，取代 agent 自報的數字。

用法：
  python _src/batch_stats.py                 # 全書
  python _src/batch_stats.py --book 02_戒疏
輸出：
  測試/真實統計.tsv
  測試/真實統計.md
"""
import glob
import io
import os
import re
import sys
from collections import defaultdict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAK = os.path.join(B, '歸檔', '7K卷修正前')
OUT = os.path.join(B, 'AI語譯', 'out')
REPORT_TSV = os.path.join(B, '測試', '真實統計.tsv')
REPORT_MD = os.path.join(B, '測試', '真實統計.md')


def read_paras(p):
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8', errors='ignore').read()) if x.strip()]


def main():
    only = None
    if '--book' in sys.argv:
        only = sys.argv[sys.argv.index('--book') + 1]

    rows = []
    for book_dir in sorted(glob.glob(os.path.join(BAK, '*'))):
        if not os.path.isdir(book_dir):
            continue
        book = os.path.basename(book_dir)
        if only and book != only:
            continue
        for bp in sorted(glob.glob(os.path.join(book_dir, '*.txt'))):
            fname = os.path.basename(bp)
            # 備份可能帶 _v/_v2/_l/_l2/_a/_b/_c/_q/_x/_y/_z/_n/_n2... 後綴
            m = re.match(r'(.+?)_(v\d?|l\d?|n\d?|[a-z]\d?|[a-z])\.txt$', fname)
            chunk = m.group(1) if m else fname[:-4]
            cp = os.path.join(OUT, book, chunk + '.txt')
            if not os.path.exists(cp):
                rows.append((book, chunk, '缺現行檔', 0, 0, 0))
                continue
            old = read_paras(bp)
            new = read_paras(cp)
            if len(old) != len(new):
                rows.append((book, chunk, '段數不符(%d/%d)' % (len(old), len(new)), 0, 0, 0))
                continue
            changed = sum(1 for a, b in zip(old, new) if a != b)
            # 改動處：以最小差異片段計
            spots = 0
            for a, b in zip(old, new):
                if a == b:
                    continue
                # 以 4 字滑窗估差異點數
                import difflib
                sm = difflib.SequenceMatcher(None, a, b)
                spots += sum(1 for op in sm.get_opcodes() if op[0] != 'equal')
            dl = sum(len(b) - len(a) for a, b in zip(old, new) if a != b)
            rows.append((book, chunk, 'ok', changed, spots, dl))

    os.makedirs(os.path.dirname(REPORT_TSV), exist_ok=True)
    with io.open(REPORT_TSV, 'w', encoding='utf-8') as f:
        f.write('書\tchunk\t狀態\t改段數\t改動處\t字數增減\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')

    agg = defaultdict(lambda: [0, 0, 0, 0])
    bad = []
    for book, chunk, st, ch, sp, dl in rows:
        if st != 'ok':
            bad.append((book, chunk, st))
            continue
        a = agg[book]
        a[0] += 1
        a[1] += ch
        a[2] += sp
        a[3] += dl

    lines = ['# 真實統計（由備份 diff 產生）', '',
             '| 書 | 檔案數 | 改段數 | 改動處 | 字數增減 |', '|:--|--:|--:|--:|--:|']
    tot = [0, 0, 0, 0]
    for book in sorted(agg):
        n, ch, sp, dl = agg[book]
        lines.append('| %s | %d | %d | %d | %+d |' % (book, n, ch, sp, dl))
        tot = [tot[0] + n, tot[1] + ch, tot[2] + sp, tot[3] + dl]
    lines.append('| **合計** | **%d** | **%d** | **%d** | **%+d** |' % tuple(tot))
    if bad:
        lines += ['', '## 異常', '']
        for b in bad:
            lines.append('- %s/%s：%s' % b)
    io.open(REPORT_MD, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    print('掃描 %d 個備份檔' % len(rows))
    for book in sorted(agg):
        n, ch, sp, dl = agg[book]
        print('  %-14s %3d 檔  改 %4d 段  處 %5d  字 %+6d' % (book, n, ch, sp, dl))
    print('  合計 %d 檔，改 %d 段，%d 處，%+d 字' % tuple(tot))
    if bad:
        print(' 異常 %d 筆（見報告）' % len(bad))


if __name__ == '__main__':
    main()