# -*- coding: utf-8 -*-
"""網站驗收。

除了原有的導覽錨點、搜尋索引、句讀密度、`<br><br>` 之外，2026-11-23 新增：
* 44 頁都要有 `footer.sitefoot` 與 `<nav class="pager">`，且都在 `</main>` 之外。
* 每卷至少 1 節；`nav.json` 節數 == 頁面 `h2.sec` 數；錨點存在。
* `id` 不得重複；每頁 1 個 `h1`。
* 頁面大小（>1.0 MB 警告、>2.5 MB 失敗）。
* 全站資源版本 == `site_assets.ASSET_VERSION`。
* `docs/style.css`、`nav.js`、`search.js` 與 `_src` 完全相同（單一來源）。
* `docs/` 不得有 `_backup*`／`_備份*` 目錄（避免被靜態伺服器服務）。
"""
import argparse
import collections
import glob
import io
import json
import os
import re
import sys

import build_search_index as BSI
import site_assets as SA

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
SIZE_WARN = 1.0 * 1024 * 1024
SIZE_FAIL = 2.5 * 1024 * 1024


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', action='append', choices=sorted(BOOKS))
    ap.add_argument('--suffix', default='', help='例如 .new：優先檢查尚未套用的頁面')
    ap.add_argument('--no-search', dest='search', action='store_false',
                    help='略過搜尋索引錨點檢查')
    args = ap.parse_args()
    books = args.book or list(BOOKS)

    nav = json.load(io.open(os.path.join(B, 'docs', 'nav.json'), encoding='utf-8'))
    navmap = {b['out']: b for b in nav['books']}
    bad, warn = [], []
    n_pages = n_anchor = n_brbr = n_punct = n_pairs = 0
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
            if not os.path.exists(p):
                bad.append(('NOFILE', book, v, p))
                continue
            t = io.open(p, encoding='utf-8').read()
            n_pages += 1
            size = len(t.encode('utf-8'))
            if size > SIZE_FAIL:
                bad.append(('SIZEFAIL', book, v, '%.2f MB' % (size / 1048576.0)))
            elif size > SIZE_WARN:
                warn.append(('SIZE', book, v, '%.2f MB' % (size / 1048576.0)))

            n = t.count('<br><br>')
            n_brbr += n
            if n:
                bad.append(('BRBR', book, v, n))

            n_pairs += t.count('<div class="pair')
            ids = re.findall(r'\bid="([^"]+)"', t)
            dup = sorted({x for x, c in collections.Counter(ids).items() if c > 1})
            if dup:
                bad.append(('DUPID', book, v, dup[:5]))
            if t.count('<h1>') != 1:
                bad.append(('H1', book, v, t.count('<h1>')))
            if t.count('<footer class="sitefoot">') != 1:
                bad.append(('FOOTER', book, v, t.count('<footer class="sitefoot">')))
            if t.count('<nav class="pager"') != 1:
                bad.append(('PAGER', book, v, t.count('<nav class="pager"')))
            else:
                if 'rel="prev"' not in t and 'rel="next"' not in t:
                    bad.append(('PAGERREL', book, v))
                if 'aria-label="卷導覽"' not in t:
                    bad.append(('PAGERLABEL', book, v))
            i_main = t.find('</main>')
            i_foot = t.find('<footer class="sitefoot">')
            i_pager = t.find('<nav class="pager"')
            if i_main >= 0:
                if i_foot >= 0 and i_foot < i_main:
                    bad.append(('FOOTERINMAIN', book, v))
                if i_pager >= 0 and i_pager < i_main:
                    bad.append(('PAGERINMAIN', book, v))
            if 'tabindex="-1"' not in t:
                bad.append(('MAINTAB', book, v))

            secs = []
            for sec in navmap.get(book, {}).get('vols', []):
                if sec['v'] == v:
                    secs = sec.get('secs') or []
            n_anchor += len(secs)
            if not secs:
                bad.append(('NOSEC', book, v))
            n_h2 = len(re.findall(r'<h2 class="sec"', t))
            if n_h2 != len(secs):
                bad.append(('SECCOUNT', book, v, n_h2, len(secs)))
            id_set = set(ids)
            for sid, label in secs:
                if sid not in id_set:
                    bad.append(('ANCHOR', book, v, sid, label))

            for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>', t, re.S):
                x = re.sub('<[^>]+>', '', m.group(1))
                if BOX.search(x):
                    continue
                if book == 'jieshu' and re.match(r'【[^】]+】【(?:目錄|條目)】', x):
                    continue
                nh = len(han(x))
                punct = len(re.findall(r'[，。；：！？、]', x))
                if nh > 30 and punct / nh < 0.01:
                    n_punct += 1
                    bad.append(('PUNCT', book, v, x[:50]))

    # 全站資源版本（所有 html，含首頁／搜尋／附錄／未譯）
    n_pages_all = 0
    if not args.suffix:
        for p in glob.glob(os.path.join(B, 'docs', '**', '*.html'), recursive=True):
            rel = os.path.relpath(p, os.path.join(B, 'docs'))
            if rel.split(os.sep)[0].startswith(('_backup', '_備份')):
                continue
            n_pages_all += 1
            t = io.open(p, encoding='utf-8').read()
            vers = set(re.findall(r'\?v=(\d+)', t))
            if vers - {SA.ASSET_VERSION}:
                bad.append(('ASSETVER', rel, sorted(vers)))
            if 'style.css?v=' not in t or 'nav.js?v=' not in t:
                bad.append(('ASSETMISS', rel))

    # 共用資源必須與 _src 完全相同（P1-8 單一來源）
    if not args.suffix:
        for name, dst in (('site.css', 'style.css'), ('nav.js', 'nav.js'), ('search.js', 'search.js')):
            a = os.path.join(B, '_src', name)
            b = os.path.join(B, 'docs', dst)
            if os.path.exists(b) and io.open(a, 'rb').read() != io.open(b, 'rb').read():
                bad.append(('ASSETDIFF', dst))

    # docs 不得有備份目錄（P1-9）
    for d in os.listdir(os.path.join(B, 'docs')):
        full = os.path.join(B, 'docs', d)
        if os.path.isdir(full) and (d.startswith('_backup') or d.startswith('_備份')):
            bad.append(('BACKUPDIR', d))

    for b in bad[:30]:
        print(b)
    for w in warn[:15]:
        print(('WARN',) + tuple(w))
    if len(warn) > 15:
        print(('WARN',) + ('...', len(warn)))

    n_search = n_search_bad = 0
    if args.search:
        counts, issues = BSI.verify(books=set(books))
        n_search = counts['entries']
        n_search_bad = len(issues)
        for it in issues[:20]:
            print(('SEARCH',) + tuple(it))

    print('pages %d (all html %d) anchors %d pairs %d brbr %d punct %d '
          'search %d searchbad %d errors %d warns %d v%s'
          % (n_pages, n_pages_all, n_anchor, n_pairs, n_brbr, n_punct,
             n_search, n_search_bad, len(bad), len(warn), SA.ASSET_VERSION))
    sys.exit(1 if (bad or n_search_bad) else 0)


if __name__ == '__main__':
    main()
