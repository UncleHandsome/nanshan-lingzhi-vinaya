# -*- coding: utf-8 -*-
"""網站驗收（一篇一頁 v62）。

頁面模型
--------
* `docs/<book>/<卷>.html`：卷目錄頁（h1＋byline＋`h2#p-toc 本卷篇目`＋篇連結；0 pair）。
* `docs/<book>/<卷>__p<N>.html`：篇頁（h1＋1 個 h2.sec＋pairs；pager 為全書篇序）。
* `docs/` 根目錄 4 個靜態頁：index／search／appendix／download。

檢查（不得放水）
----------------
* 頁面清單由 nav.json 取得；卷序＝既定書目卷序；不得有多餘 html、殘留舊篇頁。
* 卷目錄頁：1 個 h1、1 個 `h2.sec#p-toc`、0 pair、篇目清單連結與 nav 完全一致；
  footer／pager 在 `</main>` 之外；pager 為卷層級（上一卷／下一卷／目錄）。
* 篇頁：1 個 h1、1 個 h2.sec（id／標題與 nav 一致）、至少 1 pair；
  pager prev/next＝全書篇序（跨卷）且 label 正確、「目錄」連到該卷目錄頁。
* 共用：id 不重複、單頁 1 個 h1、無 `<br><br>`、無無句讀長段、頁面大小上限、
  main tabindex、無 `.new` 殘檔、docs 不得有備份目錄。
* nav 的篇連結都指到存在的篇頁；卷頁與篇頁數、全站 pair 總數、搜尋索引一致。
* 全站資源版本 == `site_assets.ASSET_VERSION`；style.css／nav.js／search.js／ui.js
  與 `_src` 完全相同（單一來源）。
* 搜尋索引 `verify()` 0 issues；索引條目都指向篇頁（不是卷目錄頁）；
  全站 search 條目數不變（EXPECT_SEARCH）。

用法
----
    python -X utf8 _src/validate_site.py
    python -X utf8 _src/validate_site.py --book hebian
"""
import argparse
import collections
import glob
import html
import io
import json
import os
import re
import sys

import build_search_index as BSI
import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DOCS = os.path.join(B, 'docs')
MAIN_OPEN = '<main id="main" tabindex="-1">'
MAIN_CLOSE = '</main>'
PAIR_OPEN = '<div class="pair'

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

STATIC_PAGES = ['index.html', 'search.html', 'appendix.html',
                'download.html', 'prompt.html']
# 一篇一頁改版前後都必須成立的兩個全站總數（不得退步）
EXPECT_PAIRS = 29937
EXPECT_SEARCH = 29913

BOX = re.compile(r'[┌┐└┘│─├┤┬┴┼]')
SIZE_WARN = 1.0 * 1024 * 1024
SIZE_FAIL = 2.5 * 1024 * 1024
H2_RE = re.compile(r'<h2 class="sec"([^>]*)>(.*?)</h2>', re.S)
ID_RE = re.compile(r'\bid="([^"]+)"')
STEM_RE = re.compile(r'^.+__p\d+\.html$')


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s or '')


def text_of(s):
    return html.unescape(strip_tags(s)).strip()


def read(p):
    return io.open(p, encoding='utf-8').read()


def main_parts(t):
    """回傳 (prefix, main_html, post)；post 由 </main> 起。"""
    i0 = t.find(MAIN_OPEN)
    if i0 < 0:
        return None, None, None
    i0 += len(MAIN_OPEN)
    i1 = t.find(MAIN_CLOSE, i0)
    if i1 < 0:
        return None, None, None
    return t[:i0], t[i0:i1], t[i1:]


def pager_of(t):
    """解析唯一 `<nav class="pager">`：回傳 (aria, {class: (href, rel, text)}, idx)。"""
    m = re.search(r'<nav class="pager"([^>]*)>(.*?)</nav>', t, re.S)
    if not m:
        return None, {}, -1
    a = re.search(r'aria-label="([^"]+)"', m.group(1))
    links = {}
    for lm in re.finditer(r'<a class="(pg\w+)"([^>]*)>(.*?)</a>', m.group(2), re.S):
        cls, attrs, txt = lm.group(1), lm.group(2), text_of(lm.group(3))
        hm = re.search(r'href="([^"]+)"', attrs)
        rm = re.search(r'rel="([^"]+)"', attrs)
        links[cls] = (hm.group(1) if hm else '', rm.group(1) if rm else '', txt)
    return (a.group(1) if a else ''), links, m.start()


def dup_ids(t):
    ids = re.findall(r'\bid="([^"]+)"', t)
    return sorted({x for x, c in collections.Counter(ids).items() if c > 1})


def common_page_checks(rel, t, bad, warn):
    """所有內文頁共通的檢查；回傳 (main, pairs, size)。"""
    size = len(t.encode('utf-8'))
    if size > SIZE_FAIL:
        bad.append(('SIZEFAIL', rel, '%.2f MB' % (size / 1048576.0)))
    elif size > SIZE_WARN:
        warn.append(('SIZE', rel, '%.2f MB' % (size / 1048576.0)))
    dup = dup_ids(t)
    if dup:
        bad.append(('DUPID', rel, dup[:5]))
    if t.count('<h1>') != 1:
        bad.append(('H1', rel, t.count('<h1>')))
    if t.count('<footer class="sitefoot">') != 1:
        bad.append(('FOOTER', rel, t.count('<footer class="sitefoot">')))
    if t.count('<nav class="pager"') != 1:
        bad.append(('PAGER', rel, t.count('<nav class="pager"')))
    if 'tabindex="-1"' not in t:
        bad.append(('MAINTAB', rel))
    if '<br><br>' in t:
        bad.append(('BRBR', rel, t.count('<br><br>')))
    prefix, main, post = main_parts(t)
    if main is None:
        bad.append(('NOMAIN', rel))
        return None, 0, size
    i_main = len(prefix)
    if post.find('<nav class="pager"') < 0:
        bad.append(('PAGERINMAIN', rel))
    if post.find('<footer class="sitefoot">') < 0:
        bad.append(('FOOTERINMAIN', rel))
    return main, t.count(PAIR_OPEN), size


def check_punct(rel, main, book, bad):
    """回傳無句讀長段數；同時把每一段記進 bad。"""
    n = 0
    for m in re.finditer(r'<div class="o[^"]*">(.*?)</div>', main, re.S):
        x = re.sub('<[^>]+>', '', m.group(1))
        if BOX.search(x):
            continue
        if book == 'jieshu' and re.match(r'【[^】]+】【(?:目錄|條目)】', x):
            continue
        nh = len(han(x))
        punct = len(re.findall(r'[，。；：、！？]', x))
        if nh > 30 and punct / nh < 0.01:
            n += 1
            bad.append(('PUNCT', rel, x[:50]))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', action='append', choices=sorted(BOOKS))
    ap.add_argument('--no-search', dest='search', action='store_false',
                    help='略過搜尋索引檢查')
    args = ap.parse_args()
    books = args.book or list(BOOKS)
    full = not args.book

    nav = json.load(io.open(os.path.join(DOCS, 'nav.json'), encoding='utf-8'))
    bookmap = {b['out']: b for b in nav.get('books', [])}
    bad, warn = [], []
    n_pages = n_anchor = n_brbr = n_punct = n_pairs = 0
    article_pages = set()          # (book, stem)
    article_meta = {}              # (book, stem) -> (vol, id, label)
    book_articles = {}             # book -> [(vol, id, label, stem)]
    toc_counts = {}                # (book, vol) -> [(href, label, n)]
    page_pairs = {}                # (book, stem) -> 實際 pair 數

    for book in books:
        vols_expected = BOOKS[book]
        nb = bookmap.get(book)
        if not nb:
            bad.append(('NOBOOK', book))
            continue
        navy = [v.get('v') for v in nb.get('vols') or []]
        if navy != vols_expected:
            bad.append(('VOLS', book, navy, vols_expected))
            continue
        # ── 收集 nav 篇頁並檢查格式 ──
        arts = []
        seen_stem = set()
        for v in nb['vols']:
            volname = v['v']
            secs = v.get('secs') or []
            if not secs:
                bad.append(('NOSEC', book, volname))
            for s in secs:
                if not (isinstance(s, (list, tuple)) and len(s) == 3):
                    bad.append(('SECFMT', book, volname, s))
                    continue
                sid, label, stem = s
                if not (sid and label and stem):
                    bad.append(('SECEMPTY', book, volname, s))
                    continue
                if not isinstance(stem, str) or not stem.startswith(volname + '__p'):
                    bad.append(('STEM', book, volname, stem))
                    continue
                if stem in seen_stem:
                    bad.append(('DUPSTEM', book, stem))
                    continue
                seen_stem.add(stem)
                arts.append((volname, sid, label, stem))
        book_articles[book] = arts
        for _vol, sid, label, stem in arts:
            article_pages.add((book, stem))
            article_meta[(book, stem)] = (_vol, sid, label)
        order_index = {stem: i for i, (_v, _i, _l, stem) in enumerate(arts)}

        # ── 卷目錄頁 ──
        for vi, volname in enumerate(vols_expected):
            rel = '%s/%s.html' % (book, volname)
            p = os.path.join(DOCS, book, volname + '.html')
            if not os.path.exists(p):
                bad.append(('NOFILE', rel))
                continue
            t = read(p)
            n_pages += 1
            main, pairs, _size = common_page_checks(rel, t, bad, warn)
            if main is None:
                continue
            n_brbr += t.count('<br><br>')
            if pairs:
                bad.append(('PAIRINTOC', rel, pairs))
            secs = H2_RE.findall(main)
            if len(secs) != 1:
                bad.append(('TOCSEC', rel, len(secs)))
            else:
                mid = ID_RE.search(secs[0][0])
                if not mid or mid.group(1) != 'p-toc':
                    bad.append(('TOCTAG', rel, mid.group(1) if mid else ''))
                if text_of(secs[0][1]) != '本卷篇目':
                    bad.append(('TOCTITLE', rel, text_of(secs[0][1])))
            # 篇目清單必須與 nav 一致
            um = re.search(r'<ul class="voltoc">(.*?)</ul>', main, re.S)
            got = []
            if um:
                for a in re.finditer(r'<li><a href="([^"]+)"><span class="tn">'
                                     r'(.*?)</span><span class="n">(\d+) 段</span>'
                                     r'</a></li>', um.group(1), re.S):
                    got.append((a.group(1), text_of(a.group(2)), int(a.group(3))))
            want = [(stem + '.html', label)
                    for (_v, _i, label, stem) in arts if _v == volname]
            got_pairs = [(h, lab) for (h, lab, _n) in got]
            if got_pairs != want:
                bad.append(('TOCLIST', rel, got_pairs[:3], want[:3]))
            if any(n <= 0 for (_h, _l, n) in got):
                bad.append(('TOCPAIRS', rel, [n for (_h, _l, n) in got if n <= 0][:5]))
            # 段數要與實際篇頁 pair 數一致（篇頁檢查後回填比對）
            toc_counts[(book, volname)] = got
            # pager：卷層級
            aria, links, _pos = pager_of(t)
            if aria != '卷導覽':
                bad.append(('PAGERLABEL', rel, aria))
            prev_v = vols_expected[vi - 1] if vi > 0 else None
            next_v = vols_expected[vi + 1] if vi + 1 < len(vols_expected) else None
            if prev_v:
                if 'pgprev' not in links or links['pgprev'][0] != prev_v + '.html':
                    bad.append(('PAGERPREV', rel, links.get('pgprev')))
            elif 'pgprev' in links:
                bad.append(('PAGERPREV', rel, links['pgprev']))
            if next_v:
                if 'pgnext' not in links or links['pgnext'][0] != next_v + '.html':
                    bad.append(('PAGERNEXT', rel, links.get('pgnext')))
            elif 'pgnext' in links:
                bad.append(('PAGERNEXT', rel, links['pgnext']))
            if 'pgidx' not in links or links['pgidx'][0] != '../index.html':
                bad.append(('PAGERIDX', rel, links.get('pgidx')))

        # ── 篇頁 ──
        for (volname, sid, label, stem) in arts:
            rel = '%s/%s.html' % (book, stem)
            p = os.path.join(DOCS, book, stem + '.html')
            if not os.path.exists(p):
                bad.append(('NOFILE', rel))
                continue
            t = read(p)
            n_pages += 1
            n_anchor += 1
            main, pairs, _size = common_page_checks(rel, t, bad, warn)
            if main is None:
                continue
            n_pairs += pairs
            n_brbr += t.count('<br><br>')
            if pairs < 1:
                bad.append(('NOPAIR', rel))
            secs = H2_RE.findall(main)
            if len(secs) != 1:
                bad.append(('ARTSEC', rel, len(secs)))
            else:
                mid = ID_RE.search(secs[0][0])
                got_id = mid.group(1) if mid else ''
                got_label = text_of(secs[0][1])
                if got_id != sid:
                    bad.append(('ARTID', rel, got_id, sid))
                if got_label != label:
                    bad.append(('ARTLABEL', rel, got_label, label))
            n_punct += check_punct(rel, main, book, bad)
            page_pairs[(book, stem)] = pairs
            # pager：全書篇序（跨卷）
            aria, links, _pos = pager_of(t)
            if aria != '篇導覽':
                bad.append(('PAGERLABEL', rel, aria))
            i = order_index[stem]
            prev_a = arts[i - 1] if i > 0 else None
            next_a = arts[i + 1] if i + 1 < len(arts) else None
            if prev_a:
                lk = links.get('pgprev')
                if not lk or lk[0] != prev_a[3] + '.html' or prev_a[2] not in lk[2]:
                    bad.append(('PAGERPREV', rel, lk, prev_a[3] + '.html', prev_a[2]))
            elif 'pgprev' in links:
                bad.append(('PAGERPREV', rel, links['pgprev']))
            if next_a:
                lk = links.get('pgnext')
                if not lk or lk[0] != next_a[3] + '.html' or next_a[2] not in lk[2]:
                    bad.append(('PAGERNEXT', rel, lk, next_a[3] + '.html', next_a[2]))
            elif 'pgnext' in links:
                bad.append(('PAGERNEXT', rel, links['pgnext']))
            if 'pgidx' not in links or links['pgidx'][0] != volname + '.html':
                bad.append(('PAGERIDX', rel, links.get('pgidx')))

        # 卷目錄頁列的段數必須等於篇頁實際 pair 數
        for volname in vols_expected:
            for (href, label, n) in toc_counts.get((book, volname), []):
                stem = href[:-5] if href.endswith('.html') else href
                if page_pairs.get((book, stem)) != n:
                    bad.append(('TOCPAIRCOUNT', '%s/%s.html' % (book, volname),
                                stem, n, page_pairs.get((book, stem))))

        # ── 殘檔／多餘頁面：book 目錄內不得有 nav 沒有的 html ──
        d = os.path.join(DOCS, book)
        expected_files = {(stem + '.html') for (_v, _i, _l, stem) in arts}
        expected_files |= {(v + '.html') for v in vols_expected}
        for f in sorted(os.listdir(d)):
            if not f.endswith('.html'):
                continue
            if f in expected_files:
                continue
            if STEM_RE.match(f):
                bad.append(('STALE', '%s/%s' % (book, f)))
            else:
                bad.append(('EXTRAHTML', '%s/%s' % (book, f)))

    # ── 全站：靜態頁、資產版本、共用資源、殘檔 ──
    n_pages_all = 0
    if full:
        for name in STATIC_PAGES:
            if not os.path.exists(os.path.join(DOCS, name)):
                bad.append(('NOSTATIC', name))
        root_html = sorted(f for f in os.listdir(DOCS) if f.endswith('.html'))
        if root_html != sorted(STATIC_PAGES):
            bad.append(('ROOTHTML', root_html))
        for p in sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True)):
            rel = os.path.relpath(p, DOCS)
            if rel.split(os.sep)[0].startswith(('_backup', '_備份')):
                continue
            n_pages_all += 1
            t = read(p)
            vers = set(re.findall(r'\?v=(\d+)', t))
            if vers - {SA.ASSET_VERSION}:
                bad.append(('ASSETVER', rel, sorted(vers)))
            if 'style.css?v=' not in t or 'nav.js?v=' not in t or 'ui.js?v=' not in t:
                bad.append(('ASSETMISS', rel))
        expect_all = n_pages + len(STATIC_PAGES)
        if n_pages_all != expect_all:
            bad.append(('PAGECOUNT', n_pages_all, expect_all))
        for name, dst in (('site.css', 'style.css'), ('nav.js', 'nav.js'),
                          ('search.js', 'search.js'), ('ui.js', 'ui.js')):
            a = os.path.join(B, '_src', name)
            b = os.path.join(DOCS, dst)
            if os.path.exists(b) and io.open(a, 'rb').read() != io.open(b, 'rb').read():
                bad.append(('ASSETDIFF', dst))
        for f in glob.glob(os.path.join(DOCS, '**', '*.new'), recursive=True):
            bad.append(('NEWFILE', os.path.relpath(f, DOCS)))
        for d in os.listdir(DOCS):
            full_d = os.path.join(DOCS, d)
            if os.path.isdir(full_d) and (d.startswith('_backup') or d.startswith('_備份')):
                bad.append(('BACKUPDIR', d))
        if n_pairs != EXPECT_PAIRS:
            bad.append(('TOTALPAIRS', n_pairs, EXPECT_PAIRS))
        n_articles_nav = sum(len(book_articles.get(bk, [])) for bk in books)
        if n_anchor != n_articles_nav:
            bad.append(('ANCHORCOUNT', n_anchor, n_articles_nav))

    # ── 搜尋索引 ──
    n_search = n_search_bad = 0
    if args.search:
        counts, issues = BSI.verify(books=set(books))
        n_search = counts['entries']
        n_search_bad = len(issues)
        for it in issues[:20]:
            print(('SEARCH',) + tuple(it))
        if full and n_search != EXPECT_SEARCH:
            bad.append(('TOTALSEARCH', n_search, EXPECT_SEARCH))
        for (bid, pg) in sorted(counts.get('page_set', ())):
            if (bid, pg) not in article_pages:
                bad.append(('IDXPAGE', bid, pg))

    for x in bad[:30]:
        print(x)
    if len(bad) > 30:
        print(('...', 'bad total', len(bad)))
    for w in warn[:15]:
        print(('WARN',) + tuple(w))
    if len(warn) > 15:
        print(('WARN',) + ('...', len(warn)))

    print('pages %d (all html %d) anchors %d pairs %d brbr %d punct %d '
          'search %d searchbad %d errors %d warns %d v%s'
          % (n_pages, n_pages_all, n_anchor, n_pairs, n_brbr, n_punct,
             n_search, n_search_bad, len(bad), len(warn), SA.ASSET_VERSION))
    sys.exit(1 if (bad or n_search_bad) else 0)


if __name__ == '__main__':
    main()
