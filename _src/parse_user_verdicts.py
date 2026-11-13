# -*- coding: utf-8 -*-
"""解析使用者 ret.txt 的裁定，抽出可套用的「改」項。"""
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '存疑材料', '待處理', 'ret.txt')
OUT = os.path.join(B, '存疑材料', '待處理', '裁定_可套用.tsv')

SEG = re.compile(r'(\d{3,4}-\d{3,4})')


def main():
    t = io.open(SRC, encoding='utf-8').read()
    # 切成條目
    blocks = re.split(r'(?m)^###\s+', t)
    rows = []
    for b in blocks[1:]:
        head, _, body = b.partition('\n')
        segs = SEG.findall(head)
        m = re.search(r'\*\*結論\*\*[：:]\s*\*\*(.+?)\*\*', body, re.S)
        if not m:
            continue
        verdict = m.group(1).strip()
        if not verdict.startswith('改'):
            continue
        # 取結論後括號內文字
        after = body[m.end():m.end() + 300]
        pairs = re.findall(r'[「『]([^」』]{1,20})[」』]\s*→\s*[「『]([^」』]{0,40})[」』]', after)
        rows.append((segs[0] if segs else '', head[:60], verdict, pairs, after[:120].replace('\n', ' ')))

    with io.open(OUT, 'w', encoding='utf-8') as f:
        f.write('段號\t標題\t結論\t原→新\t說明\n')
        for seg, head, verdict, pairs, note in rows:
            ps = '；'.join('%s→%s' % (a, b) for a, b in pairs) if pairs else ''
            f.write('\t'.join([seg, head, verdict[:40], ps, note[:100]]) + '\n')
    print('「改」條目 %d，其中含明確「原→新」對 %d' %
          (len(rows), sum(1 for r in rows if r[3])))
    print('→', OUT)
    for r in rows[:8]:
        print('  %-12s %s' % (r[0], r[3] or '（無明確對）'))


if __name__ == '__main__':
    main()