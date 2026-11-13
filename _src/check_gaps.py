# -*- coding: utf-8 -*-
"""比對「卷派工檔號清單」與「已登記 TSV 檔號」，找出未被處理的檔。

用法：
  python _src/check_gaps.py            # 全書
  python _src/check_gaps.py 資持記      # 只查一本
"""
import glob
import io
import os
import re
import sys
from collections import defaultdict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
W = os.path.join(B, 'AI語譯', '_work', 'review', '卷派工')
D = os.path.join(B, 'batch_qwen', 'r7k_done')
REPORT = os.path.join(B, '測試', '缺口掃描.md')


def read_first_col(p):
    out = []
    for line in io.open(p, encoding='utf-8', errors='ignore'):
        if not line.strip():
            continue
        f = line.split('\t')[0].strip()
        if re.fullmatch(r'\d{4}', f):
            out.append(f)
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    for vp in sorted(glob.glob(os.path.join(W, '*.tsv'))):
        vol = os.path.basename(vp)[:-4]
        book = vol.split('_')[0]
        if only and book != only:
            continue
        want = read_first_col(vp)
        if not want:
            continue
        got = set()
        # 所有屬於此卷的登記檔（含續批、缺、補救）
        vname = vol.split('_', 1)[1] if '_' in vol else vol
        for tp in glob.glob(os.path.join(D, '*.tsv')):
            tname = os.path.basename(tp)[:-4]
            if vname not in tname:
                continue
            # 避免 a/b 混淆：要求卷名完整出現
            got.update(read_first_col(tp))
        missing = [x for x in want if x not in got]
        rows.append((vol, len(want), len(got & set(want)), missing))

    lines = ['# 缺口掃描（未登記的檔）', '']
    total_missing = sum(len(r[3]) for r in rows)
    lines.append('合計缺 %d 檔' % total_missing)
    lines += ['', '| 卷 | 清單檔數 | 已登記 | 缺 |', '|:--|--:|--:|--:|']
    for vol, n, g, m in rows:
        lines.append('| %s | %d | %d | **%d** |' % (vol, n, g, len(m)))
    lines.append('')
    for vol, n, g, m in rows:
        if not m:
            continue
        lines += ['## %s（缺 %d 檔）' % (vol, len(m)), '', '```', ' '.join(m), '```', '']
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    print('缺 %d 檔，報告 %s' % (total_missing, REPORT))
    for vol, n, g, m in rows:
        if m:
            print('  %-22s 缺 %3d／%3d：%s%s' % (vol, len(m), n, ' '.join(m[:12]),
                                              ' …' if len(m) > 12 else ''))


if __name__ == '__main__':
    main()