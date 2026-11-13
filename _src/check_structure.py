# -*- coding: utf-8 -*-
"""語料結構檢查：段落壓平、行尾漂移、引號配對、段數對齊。

用法：
  python _src/check_structure.py            # 全書
  python _src/check_structure.py 資持記      # 只查一本
"""
import glob
import io
import os
import re
import subprocess
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
REPORT = os.path.join(B, '測試', '結構檢查.md')

BOOKS = ['01_行事鈔', '02_戒疏', '03_業疏', '04_比丘尼鈔', '05_拾毗尼義鈔', '資持記']


def paras_of(text):
    return [x for x in re.split(r'(?:\r?\n){2,}', text) if x.strip()]


def lines_of(text):
    return [x for x in re.split(r'\r?\n', text) if x.strip()]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    issues = {'collapse': [], 'eol': [], 'quote': [], 'count': []}

    for book in BOOKS:
        if only and book != only:
            continue
        d = os.path.join(OUT, book)
        if not os.path.isdir(d):
            continue
        src_dir = {
            '01_行事鈔': 'TXT_分卷/01_行事鈔',
            '02_戒疏': 'TXT_分卷/02_戒疏',
            '03_業疏': 'TXT_分卷_標點/03_業疏',
            '04_比丘尼鈔': 'TXT_分卷/04_比丘尼鈔',
            '05_拾毗尼義鈔': 'TXT_分卷/05_拾毗尼義鈔',
            '資持記': 'TXT_分卷/資持記_細分',
        }[book]
        sd = os.path.join(B, src_dir.replace('/', os.sep))

        for p in sorted(glob.glob(os.path.join(d, '*.txt'))):
            name = os.path.basename(p)
            raw = open(p, 'rb').read()
            text = raw.decode('utf-8', errors='ignore')
            ps, ls = paras_of(text), lines_of(text)

            # 1) 段落壓平：段落數遠少於非空行數
            if ps and len(ps) < len(ls) * 0.8:
                issues['collapse'].append((book, name, len(ps), len(ls)))

            # 2) 行尾 vs git HEAD
            r = subprocess.run(['git', 'show', 'HEAD:AI語譯/out/%s/%s' % (book, name)],
                               cwd=B, capture_output=True)
            if r.returncode == 0:
                if (b'\r\n' in r.stdout) != (b'\r\n' in raw):
                    issues['eol'].append((book, name,
                                          'CRLF' if b'\r\n' in r.stdout else 'LF'))

            # 3) 引號配對（逐段）
            for i, x in enumerate(ps, 1):
                if x.count('「') != x.count('」') or x.count('『') != x.count('』'):
                    issues['quote'].append((book, name, i, x[:40]))
                    break

            # 4) 段數 vs 原文
            sp = os.path.join(sd, name)
            if os.path.exists(sp):
                sraw = io.open(sp, encoding='utf-8', errors='ignore').read().split('\n')
                src = [x.strip() for x in (sraw[5:] if book != '03_業疏' else sraw) if x.strip()]
                if len(src) != len(ps):
                    issues['count'].append((book, name, len(src), len(ps)))

    lines = ['# 語料結構檢查', '']
    total = sum(len(v) for v in issues.values())
    lines.append('問題總數：**%d**' % total)
    for key, title in (('collapse', '段落壓平'), ('count', '段數不符'),
                       ('eol', '行尾漂移'), ('quote', '引號不配')):
        v = issues[key]
        lines += ['', '## %s（%d）' % (title, len(v)), '']
        if not v:
            lines.append('（無）')
        for item in v[:60]:
            lines.append('- ' + ' ｜ '.join(str(x) for x in item))
        if len(v) > 60:
            lines.append('- …其餘 %d 項' % (len(v) - 60))
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    print('問題總數 %d' % total)
    for key, title in (('collapse', '段落壓平'), ('count', '段數不符'),
                       ('eol', '行尾漂移'), ('quote', '引號不配')):
        print('  %-8s %d' % (title, len(issues[key])))
    print('報告：', REPORT)
    for item in issues['collapse'][:5]:
        print('  ⚠', item)


if __name__ == '__main__':
    main()