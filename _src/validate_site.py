# -*- coding: utf-8 -*-
"""網站驗收：導覽錨點必須存在，長原文必須有句讀，且不得有 <br><br>。"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
    'xingshichao': ['卷上', '卷中', '卷下'],
    'jieshu': ['卷一', '卷二', '卷三', '卷四'],
    'yeshu': ['卷一', '卷二', '卷三', '卷四'],
    'nicao': ['卷上', '卷中', '卷下'],
    'yichao': ['卷上', '卷中'],
    'zhichi': ['上一上', '上一下', '上二', '上三', '上四',
               '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
               '下一', '下二', '下三', '下四'],
    'hebian': ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
               '卷中之一', '卷中之二', '卷中之三', '卷中之四',
               '卷下之一', '卷下之二', '卷下之三', '卷下之四'],
}
BOX = re.compile(r'[┌┐└┘│─├┤┬┴┼]')


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', action='append', choices=sorted(BOOKS))
    ap.add_argument('--suffix', default='', help='例如 .new：優先檢查尚未套用的頁面')
    args = ap.parse_args()
    books = args.book or list(BOOKS)

    nav = json.load(io.open(os.path.join(B, 'docs', 'nav.json'), encoding='utf-8'))
    navmap = {b['out']: b for b in nav['books']}
    bad = []
    n_pages = n_anchor = n_brbr = n_punct = 0
    for book in books:
        for v in BOOKS[book]:
            p = os.path.join(B, 'docs', book, v + '.html')
            if args.suffix:
                q = p + args.suffix
                if os.path.exists(q):
                    p = q
                else:
                    bad.append(('NOFILE', book, v, p + args.suffix))
                    continue
            t = io.open(p, encoding='utf-8').read()
            n_pages += 1

            n = t.count('<br><br>')
            n_brbr += n
            if n:
                bad.append(('BRBR', book, v, n))

            ids = set(re.findall(r'id="([^"]+)"', t))
            for sec in navmap.get(book, {}).get('vols', []):
                if sec['v'] == v:
                    for sid, label in sec['secs']:
                        n_anchor += 1
                        if sid not in ids:
                            bad.append(('ANCHOR', book, v, sid, label))
            for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>', t, re.S):
                x = re.sub('<[^>]+>', '', m.group(1))
                if BOX.search(x):
                    continue
                # 戒疏目錄／條目是列表，不是長句，不套句讀密度檢查
                if book == 'jieshu' and re.match(r'【[^】]+】【(?:目錄|條目)】', x):
                    continue
                nh = len(han(x))
                punct = len(re.findall(r'[，。；：！？、]', x))
                if nh > 30 and punct / nh < 0.01:
                    n_punct += 1
                    bad.append(('PUNCT', book, v, x[:50]))

    for b in bad[:20]:
        print(b)
    print('pages %d anchors %d brbr %d punct %d issues %d'
          % (n_pages, n_anchor, n_brbr, n_punct, len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
