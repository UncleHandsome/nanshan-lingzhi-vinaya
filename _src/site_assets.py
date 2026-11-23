# -*- coding: utf-8 -*-
"""全站共用頁面骨架、導覽與資源版本。

這個模組只負責產生字串，不讀寫檔案，讓 site2.py / site_hebian.py 都能安全 import。

2026-11-23 版：
* `</main>` 之後才放卷末導覽與頁尾（頁面生成器只換 `<main>` 也不會再吃掉它們）。
* 卷末導覽是 `<nav class="pager">` landmark，含 rel="prev"/"next"。
* `<main tabindex="-1">` 讓 skip link 真的能把焦點移進正文。
* 內容頁加閱讀工具列（原文／白話切換、雙欄對照、複製本段連結）。
"""
import html

ASSET_VERSION = '21'

FOOTER = (
    '<footer class="sitefoot">'
    '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯：本站自製。'
    '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權：'
    '姓名標示－非商業性－相同方式分享。轉載請保留出處，且不得作商業使用。'
    '<br><a href="ROOTLICENSE">授權全文</a></footer>'
)

_HEAD_SCRIPT = (
    '<script>try{var h=document.documentElement,m=localStorage.getItem("dsh-read-mode")||"";'
    'if(m==="o")h.classList.add("hide-t");else if(m==="t")h.classList.add("hide-o");'
    'if(localStorage.getItem("dsh-twocol")==="1")h.classList.add("twocol");}catch(e){}</script>'
)


def asset(prefix, name):
    """帶快取版本的資源路徑。"""
    return '%s%s?v=%s' % (prefix, name, ASSET_VERSION)


def uid(prefix, key, suffix=''):
    """由定稿 key 產生穩定、可用於 URL 的 id（只留 ASCII）。

    `01a_卷一之一_0001` + prefix 'u' → `u01a-0001`；同一 unit 多段再加 `-2`。
    key 完全沒有 ASCII 時回空字串，呼叫端退回 pair-N。
    """
    import re
    s = re.sub(r'[^0-9A-Za-z]+', '-', str(key or '')).strip('-')
    if not s:
        return ''
    return '%s%s%s' % (prefix, s, ('-' + str(suffix)) if suffix not in ('', None) else '')


def pager_html(prev_url, next_url, prev_label, next_label, index_url):
    """卷末導覽：`<nav>` landmark，首末卷允許單邊。"""
    e = html.escape
    parts = ['<nav class="pager" aria-label="卷導覽">']
    if prev_url:
        parts.append('<a class="pgprev" rel="prev" href="' + prev_url + '">← '
                     + e(prev_label or '上一卷') + '</a>')
    parts.append('<a class="pgidx" href="' + index_url + '">目錄</a>')
    if next_url:
        parts.append('<a class="pgnext" rel="next" href="' + next_url + '">'
                     + e(next_label or '下一卷') + ' →</a>')
    parts.append('</nav>')
    return ''.join(parts)


def tools_html():
    """內容頁閱讀工具列：顯示模式、雙欄對照、複製本段連結；可收合。"""
    return (
        '<div class="readtools" role="group" aria-label="閱讀設定">'
        '<button type="button" class="rtmenu" data-menu-toggle aria-label="開合目錄">☰ 目錄</button>'
        '<button type="button" class="rttoggle" data-tools-toggle aria-expanded="true">閱讀工具</button>'
        '<div class="rtbody">'
        '<span class="rtlabel">顯示</span>'
        '<button type="button" data-read="both" aria-pressed="true" title="原文與白話上下並列">原文＋白話</button>'
        '<button type="button" data-read="o" aria-pressed="false" title="只顯示原文">原文</button>'
        '<button type="button" data-read="t" aria-pressed="false" title="只顯示白話">白話</button>'
        '<span class="rtsep" aria-hidden="true"></span>'
        '<button type="button" data-twocol-toggle aria-pressed="false" title="原文與白話左右並排，需寬螢幕">並排</button>'
        '<button type="button" data-copy-anchor>複製本段連結</button>'
        '</div>'
        '</div>'
    )


def nav_parts(prefix='', prev_url=None, next_url=None,
              prev_label=None, next_label=None, current_label=None):
    """回傳 (preamble, sidebar)：preamble 在 .wrap 之前，sidebar 在 .wrap 內。"""
    e = html.escape
    head = [
        '<a class="skip-link" href="#main">跳至正文</a>',
        '<button id="sideopen" class="sideopen" type="button" aria-controls="sidebar" aria-expanded="false" aria-label="展開目錄">目錄</button>',
        '<header class="mobilebar">',
        '<button id="navtoggle" class="iconbtn" type="button" aria-controls="sidebar" aria-expanded="false" aria-label="開啟目錄">☰</button>',
        '<a class="mobiletitle" href="' + prefix + 'index.html">南山律典</a>',
        '<span class="mobilewhere">' + e(current_label or '') + '</span>',
        '<a class="iconbtn" href="' + prefix + 'search.html" aria-label="全文搜尋">搜尋</a>',
        '</header>',
        '<div class="navscrim" id="navscrim" hidden></div>',
    ]
    parts = [
        '<nav id="sidebar" aria-label="全書目錄">',
        '<div class="navhead"><p class="brand"><a href="' + prefix + 'index.html">南山律典・白話對照</a></p>'
        '<button id="navclose" class="iconbtn" type="button" aria-label="關閉目錄">×</button>'
        '<button id="navcollapse" class="navcollapse" type="button" aria-label="收合目錄" aria-expanded="true">⟨</button></div>',
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
    parts.append('<div id="navtree" data-root="' + prefix + '" '
                 'data-nav-version="' + ASSET_VERSION + '">'
                 '<noscript><a href="' + prefix + 'index.html">目錄</a></noscript></div>')
    parts.append('</nav>')
    return ''.join(head), ''.join(parts)


def nav_html(prefix='', prev_url=None, next_url=None,
             prev_label=None, next_label=None, current_label=None):
    """相容用法：preamble ＋ sidebar。"""
    return ''.join(nav_parts(prefix, prev_url, next_url, prev_label, next_label, current_label))


def page(title, body, prefix='', prev_url=None, next_url=None,
         prev_label=None, next_label=None, current_label=None,
         extra_scripts=None, extra_head='', pager=False, tools=False,
         index_url=None, description=None):
    """完整 HTML 頁面。

    `body` 是 `<main>` 內容；卷末導覽與頁尾一律排在 `</main>` 之後，
    所以只替換 `<main>` 的生成器不會把它們吃掉。
    """
    e = html.escape
    nav_head, sidebar = nav_parts(prefix, prev_url, next_url, prev_label, next_label, current_label)
    if pager:
        pager_s = pager_html(prev_url, next_url, prev_label, next_label,
                             index_url or (prefix + 'index.html'))
    else:
        pager_s = ''
    if tools:
        body = tools_html() + body
    scripts = ['nav.js'] + list(extra_scripts or [])
    tags = ''.join('<script defer src="' + asset(prefix, s) + '"></script>' for s in scripts)
    desc = ('<meta name="description" content="' + e(description) + '">') if description else ''
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + e(title) + '｜南山律典・白話對照</title>'
        + desc +
        '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
        '<meta name="citation_author" content="UncleHandsome">'
        '<link rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">'
        '<link rel="stylesheet" href="' + asset(prefix, 'style.css') + '">'
        + _HEAD_SCRIPT + tags + extra_head + '</head><body>'
        + nav_head + '<div class="wrap">' + sidebar + '<div class="content">'
        + '<main id="main" tabindex="-1">' + body + '</main>'
        + pager_s + FOOTER.replace('ROOT', prefix)
        + '</div></div></body></html>'
    )
