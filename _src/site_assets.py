# -*- coding: utf-8 -*-
"""全站共用頁面骨架、導覽與資源版本。

這個模組只負責產生字串，不讀寫檔案，讓 site2.py / site_hebian.py 都能安全 import。
"""
import html

ASSET_VERSION = '11'

FOOTER = (
    '<footer class="sitefoot">'
    '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯：本站自製。'
    '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權：'
    '姓名標示－非商業性－相同方式分享。轉載請保留出處，且不得作商業使用。'
    '<br><a href="ROOTLICENSE">授權全文</a></footer>'
)


def asset(prefix, name):
    """帶快取版本的資源路徑。"""
    return '%s%s?v=%s' % (prefix, name, ASSET_VERSION)


def nav_html(prefix='', prev_url=None, next_url=None,
             prev_label=None, next_label=None, current_label=None):
    """回傳 skip link、行動頂欄、遮罩與側欄。"""
    e = html.escape
    parts = [
        '<a class="skip-link" href="#main">跳至正文</a>',
        '<header class="mobilebar">',
        '<button id="navtoggle" class="iconbtn" type="button" aria-controls="sidebar" aria-expanded="false" aria-label="開啟目錄">☰</button>',
        '<a class="mobiletitle" href="' + prefix + 'index.html">南山律典</a>',
        '<span class="mobilewhere">' + e(current_label or '') + '</span>',
        '<a class="iconbtn" href="' + prefix + 'search.html" aria-label="全文搜尋">搜尋</a>',
        '</header>',
        '<div class="navscrim" id="navscrim" hidden></div>',
        '<div class="wrap">',
        '<nav id="sidebar" aria-label="全書目錄">',
        '<div class="navhead"><h1><a href="' + prefix + 'index.html">南山律典・白話對照</a></h1>'
        '<button id="navclose" class="iconbtn" type="button" aria-label="關閉目錄">×</button></div>',
        '<div class="grp"><b>全書</b>'
        '<a href="' + prefix + 'index.html">目錄</a>'
        '<a href="' + prefix + 'search.html">全文搜尋</a>'
        '<a href="' + prefix + 'appendix.html">附錄</a>'
        '<a href="' + prefix + 'untranslated.html">未譯清單</a></div>',
    ]
    if prev_url or next_url:
        parts.append('<div class="grp"><b>分卷</b>')
        if prev_url:
            parts.append('<a href="' + prev_url + '">← ' + e(prev_label or '上一卷') + '</a>')
        if next_url:
            parts.append('<a href="' + next_url + '">' + e(next_label or '下一卷') + ' →</a>')
        parts.append('</div>')
    parts.append('<div class="grp navbookgrp"><b>書目</b>'
                 '<div class="tree" id="navtree" data-root="' + prefix + '" '
                 'data-nav-version="' + ASSET_VERSION + '">'
                 '<noscript><a href="' + prefix + 'index.html">目錄</a></noscript></div></div>')
    parts.append('</nav>')
    return ''.join(parts)


def page(title, body, prefix='', prev_url=None, next_url=None,
         prev_label=None, next_label=None, current_label=None,
         extra_scripts=None, extra_head=''):
    """完整 HTML 頁面；body 不含 main 包裝與頁尾。"""
    e = html.escape
    nav = nav_html(prefix, prev_url, next_url, prev_label, next_label, current_label)
    scripts = ['nav.js'] + list(extra_scripts or [])
    tags = ''.join('<script defer src="' + asset(prefix, s) + '"></script>' for s in scripts)
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + e(title) + '｜南山律典・白話對照</title>'
        '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
        '<meta name="citation_author" content="UncleHandsome">'
        '<link rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">'
        '<link rel="stylesheet" href="' + asset(prefix, 'style.css') + '">'
        + tags + extra_head + '</head><body>'
        + nav + '<main id="main">' + body + FOOTER.replace('ROOT', prefix)
        + '</main></div></body></html>'
    )
