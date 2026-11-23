# -*- coding: utf-8 -*-
"""重建不屬於六書／合編的靜態頁，並同步共用資源。

涵蓋：
* docs/index.html        目錄（由 nav.json 產生書卡，書名與 h1／nav 同源）
* docs/search.html       全文搜尋（合編預設不載入、錯誤 role=alert）
* docs/untranslated.html 未譯清單（由實際頁面統計，校勘另列）
* docs/appendix.html     附錄（只重包頁殼，表格補 caption／scope）
* docs/style.css、nav.js、search.js 由 _src 複製

用法：
    python -X utf8 _src/render_static.py
"""
import html
import io
import json
import os
import re
import shutil

import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')
SRC = os.path.join(B, '_src')

BOOKS = [
    ('xingshichao', '四分律刪繁補闕行事鈔', '唐·道宣律師　撰'),
    ('jieshu', '四分律含注戒本疏行宗記', '唐·道宣律師　疏／宋·元照律師　記'),
    ('yeshu', '四分律刪補隨機羯磨疏', '唐·道宣律師　疏／宋·元照律師　記'),
    ('zhichi', '四分律行事鈔資持記', '宋·元照律師　·　行事鈔之註'),
    ('nicao', '四分比丘尼鈔', '唐·道宣律師　述'),
    ('yichao', '四分律拾毗尼義鈔', '唐·道宣律師　撰'),
    ('hebian', '四分律行事鈔資持記・句級合編', '鈔文與記文逐段並列'),
]
TITLES = {b[0]: b[1] for b in BOOKS}
AUTHORS = {b[0]: b[2] for b in BOOKS}


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


def load_nav():
    return json.load(io.open(os.path.join(SITE, 'nav.json'), encoding='utf-8'))


def main_body(path):
    t = rd(path)
    m = re.search(r'<main\b[^>]*>(.*)</main>', t, re.S)
    if not m:
        raise SystemExit('找不到 <main>：' + path)
    body = m.group(1)
    body = re.sub(r'<nav class="pager".*?</nav>', '', body, flags=re.S)
    body = re.sub(r'<footer class="sitefoot">.*?</footer>', '', body, flags=re.S)
    return t, body


# ── 目錄 ────────────────────────────────────────────────────
def build_index(nav):
    parts = [
        '<h1>南山律典・白話對照</h1>',
        '<form class="homefind" action="search.html" method="get" role="search">'
        '<input type="search" name="q" placeholder="搜尋全站：羯磨、波羅夷、安居…" aria-label="全文搜尋">'
        '<button type="submit">全文搜尋</button></form>',
        '<p class="hint">站內全文：<code>Ctrl/⌘ K</code>；瀏覽器尋找仍用 <code>Ctrl/⌘ F</code>。</p>',
        '<p class="intro">道宣律師三大部與相關鈔疏的白話對照本，逐段原文與白話並列；'
        '原文採 CBETA 電子佛典（大正藏／卍續藏）。</p>',
        '<p class="intro"><a href="appendix.html">附錄：名相與度量衡</a>　·　'
        '<a href="untranslated.html">未譯段落清單</a></p>',
    ]
    by_out = {}
    for b in nav.get('books', []):
        out, title = b.get('out'), b.get('title') or TITLES.get(b.get('out'), '')
        vols = [v.get('v') for v in b.get('vols', []) if v.get('v')]
        if not out or not vols:
            continue
        links = ''.join('<a href="%s/%s.html">%s</a>' % (out, v, html.escape(v)) for v in vols)
        author = AUTHORS.get(out, '')
        by = (html.escape(author) + '　·　' if author else '') + '%d 卷' % len(vols)
        by_out[out] = ('<section class="card"><h2>%s</h2><p class="byline">%s</p>'
                       '<div class="grp">%s</div></section>'
                       % (html.escape(title), by, links))
    left = ''.join(by_out[x] for x in ('xingshichao', 'yeshu', 'nicao', 'yichao') if x in by_out)
    right = ''.join(by_out[x] for x in ('jieshu', 'zhichi', 'hebian') if x in by_out)
    parts.append('<div class="home-grid"><div class="home-col">%s</div>'
                 '<div class="home-col">%s</div></div>' % (left, right))
    return SA.page('目錄', ''.join(parts), body_class='page-home',
                   book_short='目錄', book_label='南山律典・白話對照',
                   description='南山律典白話對照：行事鈔、戒疏、業疏、資持記、尼鈔、義鈔與句級合編。')


# ── 搜尋 ────────────────────────────────────────────────────
def build_search(nav):
    opts = ''.join('<option value="%s">%s</option>'
                   % (html.escape(b.get('out', '')), html.escape(b.get('title', '')))
                   for b in nav.get('books', []))
    body = ('<h1>全文搜尋</h1>'
            '<p class="byline">站內全文：<code>Ctrl/⌘ K</code>；瀏覽器尋找仍用 '
            '<code>Ctrl/⌘ F</code>。可用 ↑↓ 選擇結果、Enter 開啟。</p>'
            '<p class="hint searchnav">全站：<a href="index.html">目錄</a> · '
            '<a href="appendix.html">附錄</a> · '
            '<a href="untranslated.html">未譯清單</a></p>'
            '<div class="searchbar">'
            '<input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" '
            'autocomplete="off" autofocus aria-label="全文搜尋">'
            '<select id="bookfilter" aria-label="限定書籍"><option value="">全部書籍</option>'
            + opts + '</select></div>'
            '<label class="searchopt"><input type="checkbox" id="withhebian"> '
            '包含合編（對讀本；預設不載入，避免與單書重複）</label>'
            '<p class="byline" id="count"></p>'
            '<p id="searchstatus" class="sr-only" role="status" aria-live="polite"></p>'
            '<div id="searcherror" role="alert" hidden></div>'
            '<div id="quickhits" hidden></div>'
            '<div id="hits"></div>')
    return SA.page('搜尋', body, extra_scripts=['search/manifest.js', 'search.js'],
                   book_short='全文搜尋', book_label='全站全文搜尋',
                   body_class='page-search',
                   description='全站全文搜尋：經文原文與白話逐段比對。')


# ── 未譯清單 ────────────────────────────────────────────────
def scan_pages(nav):
    total_pairs = missing = 0
    missing_pages = []
    for b in nav.get('books', []):
        out = b.get('out')
        for v in b.get('vols', []):
            p = os.path.join(SITE, out or '', (v.get('v') or '') + '.html')
            if not os.path.exists(p):
                continue
            t = rd(p)
            n = t.count('<div class="pair')
            m = len(re.findall(r'class="pair[^"]*\bmissing\b', t))
            total_pairs += n
            missing += m
            if m:
                missing_pages.append((out, v.get('v'), m))
    return total_pairs, missing, missing_pages


def build_untranslated(nav):
    total_pairs, missing, missing_pages = scan_pages(nav)
    # 資持記卷末校勘：定稿 4182 筆 − 上站 4157 段 = 25 筆（依 AGENTS 0.5 不譯、不上站）
    zrows = sum(1 for x in io.open(os.path.join(B, '定稿', 'zhichi.jsonl'), encoding='utf-8')
                if x.strip())
    zpairs = 0
    for v in [x.get('v') for x in next(b for b in nav['books'] if b.get('out') == 'zhichi')['vols']]:
        p = os.path.join(SITE, 'zhichi', v + '.html')
        if os.path.exists(p):
            zpairs += rd(p).count('<div class="pair')
    skipped = max(0, zrows - zpairs)
    parts = ['<h1>未譯段落清單</h1>',
             '<p class="byline">全書逐段比對「原文／白話」的結果，數字由實際頁面統計</p>',
             '<div class="intro"><p>目前未譯段落：<b>%d</b> 段（頁面上 <code>.pair.missing</code> 共 %d 段）。</p>'
             % (missing, missing),
             '<p>上站段落總數：<b>%d</b> 段；每一段原文都已附白話。</p>' % total_pairs]
    if missing_pages:
        parts.append('<p>有未譯段的頁面：</p><ul>')
        for out, v, m in missing_pages:
            parts.append('<li><a href="%s/%s.html">%s　%s</a>：%d 段</li>'
                         % (out, v, html.escape(TITLES.get(out, out)), html.escape(v), m))
        parts.append('</ul>')
    parts.append('<p>另有資持記卷末校勘 <b>%d</b> 筆（定稿 %d 筆 − 上站 %d 段），'
                 '依規則不譯、不上站，不是「未譯」：key %d–%d。</p>'
                 % (skipped, zrows, zpairs, 4182 - skipped + 1, 4182))
    parts.append('<p>空譯段落不會再被靜默丟棄：生成器會輸出「（本段尚未白話）」並計入上表。</p>')
    parts.append('</div>')
    return SA.page('未譯段落清單', ''.join(parts),
                   book_short='未譯清單', book_label='未譯段落清單',
                   description='未譯段落統計：由頁面實際資料計算。')


# ── 附錄 ────────────────────────────────────────────────────
def add_table_a11y(body):
    """表格補 <caption>（取最近 h2／h3）與 <th scope="col">。"""
    out, last = [], 0
    h2 = h3 = ''
    for m in re.finditer(r'<h2\b[^>]*>(.*?)</h2>|<h3\b[^>]*>(.*?)</h3>|<table\b[^>]*>', body, re.S):
        tag = m.group(0)
        if tag.startswith('<h2'):
            h2 = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            h3 = ''
            continue
        if tag.startswith('<h3'):
            h3 = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            continue
        end = body.find('</table>', m.end())
        if end < 0:
            continue
        end += len('</table>')
        block = body[m.start():end]
        # 可重複執行：先移除舊 caption／scope 再補一次
        block = re.sub(r'<caption>.*?</caption>', '', block, flags=re.S)
        cap = '　'.join(x for x in (h2, h3) if x)
        block = re.sub(r'<table\b[^>]*>',
                       lambda mm: mm.group(0) + ('<caption>%s</caption>' % html.escape(cap) if cap else ''),
                       block, count=1)
        block = re.sub(r'\s+scope="col"', '', block)
        block = re.sub(r'<th(?=[\s>])', '<th scope="col"', block)
        out.append(body[last:m.start()])
        out.append(block)
        last = end
    out.append(body[last:])
    return ''.join(out)


def build_appendix():
    path = os.path.join(SITE, 'appendix.html')
    t, body = main_body(path)
    body = add_table_a11y(body)
    m = re.search(r'<style\b[^>]*>.*?</style>', t, re.S)
    extra_head = m.group(0) if m else ''
    return SA.page('附錄：名相、音注與度量衡', body, extra_head=extra_head,
                   book_short='附錄', book_label='附錄：名相、音注與度量衡',
                   description='南山三大部白話對照本附錄：名相、音注與度量衡換算。')


# ── 共用資源 ────────────────────────────────────────────────
def copy_assets():
    for name in ('site.css', 'nav.js', 'search.js'):
        dst = 'style.css' if name == 'site.css' else name
        shutil.copyfile(os.path.join(SRC, name), os.path.join(SITE, dst))
        print('copied %s -> %s' % (name, dst))


def main():
    nav = load_nav()
    wr(os.path.join(SITE, 'index.html'), build_index(nav))
    print('index.html')
    wr(os.path.join(SITE, 'search.html'), build_search(nav))
    print('search.html')
    copy_assets()
    wr(os.path.join(SITE, 'untranslated.html'), build_untranslated(nav))
    print('untranslated.html')
    wr(os.path.join(SITE, 'appendix.html'), build_appendix())
    print('appendix.html')


if __name__ == '__main__':
    main()
