# -*- coding: utf-8 -*-
"""統計本輪實際改寫的段落數（忽略段首【…】標籤差異）。"""
import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAK = os.path.join(B, 'AI語譯', '_bak_20261105_2030', 'out')
CUR = os.path.join(B, 'AI語譯', 'out')
LEAD = re.compile(r'^(【[^】]{1,6}】)+')


def strip_lab(s):
    return LEAD.sub('', s).strip()


def paras(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main():
    tot = files = 0
    bybook = {}
    for bk in sorted(os.listdir(CUR)):
        d = os.path.join(CUR, bk)
        if not os.path.isdir(d) or bk.startswith('_'):
            continue
        n = 0
        for f in sorted(os.listdir(d)):
            if not f.endswith('.txt'):
                continue
            a = paras(os.path.join(BAK, bk, f))
            b = paras(os.path.join(d, f))
            if len(a) != len(b):
                print('!! count differs', bk, f, len(a), len(b))
                continue
            k = sum(1 for x, y in zip(a, b) if strip_lab(x) != strip_lab(y))
            if k:
                files += 1
                n += k
        if n:
            bybook[bk] = n
            tot += n
    print('content-changed paragraphs', tot, 'in files', files)
    for k, v in bybook.items():
        print('  %-12s %d' % (k, v))


if __name__ == '__main__':
    main()
