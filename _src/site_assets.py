# -*- coding: utf-8 -*-
"""全站共用頁面骨架、導覽與資源版本。

這個模組只負責產生字串，不讀寫檔案，讓 site2.py / site_hebian.py 都能安全 import。

2026-11-23 導覽重整（v22）
--------------------------
* 全站（首頁／搜尋／附錄／未譯／六書／合編）共用一個 sticky 頂部列
  `.topbar`：左「☰ 目錄」、中書卷麵包屑、右「閱讀工具／搜尋」。
* 閱讀工具由主文內移到頂部列的下拉面板，不再佔用正文，也不再壓在手機底部。
* 桌面側欄預設展開；只有區塊夠寬時才用固定側欄，窄螢幕自動變抽屜。
* 側欄收合後一定留著固定的重新開啟控制：頂部「☰ 目錄」＋左緣 `.edgepeek`
  （hover／focus 立即以浮層露出側欄）。
* 首頁與所有頁面用同一套 shell；首頁的 ☰ 不再依賴 `.readtools`。
"""
import html

ASSET_VERSION = '25'

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
    """頂部列「閱讀工具」下拉面板：顯示模式、雙欄對照、複製本段連結。

    面板由頂部列的按鈕開合；單排緊湊排列（約 420×36），不再固定佔用正文或手機底部。
    """
    return (
        '<div class="toolpanel readtools" id="toolpanel" role="group" aria-label="閱讀設定" hidden>'
        '<div class="tp-row" role="group" aria-label="顯示模式">'
        '<button type="button" data-read="both" aria-pressed="true" title="原文與白話上下並列">原文＋白話</button>'
        '<button type="button" data-read="o" aria-pressed="false" title="只顯示原文">只原文</button>'
        '<button type="button" data-read="t" aria-pressed="false" title="只顯示白話">只白話</button>'
        '</div>'
        '<span class="tp-div" aria-hidden="true"></span>'
        '<button type="button" data-twocol-toggle aria-pressed="false" title="原文與白話左右並排，需寬螢幕">並排</button>'
        '<button type="button" data-copy-anchor title="複製目前段落的網址">複製本段連結</button>'
        '</div>'
    )


def topbar_html(prefix='', current_label=None, book_label=None, book_short=None,
                tools=False):
    """全站共用頂部列：☰ 目錄／書卷／全域搜尋／更多／閱讀工具。

    全域搜尋：≥1200px 顯示 compact 輸入框（Enter 送 search.html），窄螢幕退回「搜尋」按鈕。
    「更多」收納原本佔用側欄頂端的全書連結（目錄／全文搜尋／附錄／未譯清單）。
    """
    e = html.escape
    crumb = ['<a class="tb-home" href="' + prefix + 'index.html">南山律典</a>']
    if book_short:
        title_attr = (' title="%s"' % e(book_label)) if book_label else ''
        crumb.append('<span class="tb-sep tb-sep-home" aria-hidden="true">›</span>')
        crumb.append('<span class="tb-book"' + title_attr + '>' + e(book_short) + '</span>')
    if current_label:
        if book_short:
            crumb.append('<span class="tb-sep" aria-hidden="true">·</span>')
        crumb.append('<span class="tb-where">' + e(current_label) + '</span>')

    tools_btn = ''
    if tools:
        tools_btn = (
            '<button id="toolstoggle" class="tb-btn tb-tools" type="button" '
            'data-tools-toggle aria-controls="toolpanel" aria-expanded="false" '
            'aria-label="開合閱讀工具" title="閱讀工具：顯示模式、並排、複製本段連結">'
            '<span class="tb-tools-long">閱讀工具</span><span class="tb-tools-short">工具</span></button>'
        )

    search = (
        '<form class="tb-searchform" action="' + prefix + 'search.html" method="get" role="search">'
        '<input id="tbq" name="q" type="search" placeholder="全站搜尋…" autocomplete="off" '
        'aria-label="全站全文搜尋" title="輸入關鍵字後按 Enter（Ctrl/⌘ K）">'
        '</form>'
        '<a class="tb-btn tb-searchbtn" href="' + prefix + 'search.html" '
        'aria-label="全文搜尋" title="全文搜尋（Ctrl/⌘ K）">搜尋</a>'
    )

    more = (
        '<details class="tb-more">'
        '<summary class="tb-btn tb-morebtn" aria-label="更多本站連結" '
        'title="更多：目錄、全文搜尋、附錄、未譯清單">更多</summary>'
        '<div class="tb-morepanel">'
        '<a href="' + prefix + 'index.html">目錄</a>'
        '<a href="' + prefix + 'search.html">全文搜尋</a>'
        '<a href="' + prefix + 'appendix.html">附錄</a>'
        '<a href="' + prefix + 'untranslated.html">未譯清單</a>'
        '</div></details>'
    )

    return (
        '<a class="skip-link" href="#main">跳至正文</a>'
        '<header class="topbar">'
        '<button id="navtoggle" class="tb-btn tb-menu" type="button" aria-controls="sidebar" '
        'aria-expanded="true" aria-label="開合目錄" title="開合目錄（[ 或 Alt+M）">'
        '<span class="tb-ico" aria-hidden="true">☰</span><span class="tb-menulabel">目錄</span></button>'
        '<div class="tb-crumb">' + ''.join(crumb) + '</div>'
        '<div class="tb-right">' + search + more + tools_btn + '</div>'
        + (tools_html() if tools else '')
        + '</header>'
        '<button id="edgepeek" class="edgepeek" type="button" aria-controls="sidebar" '
        'aria-label="顯示目錄" title="顯示目錄：滑鼠移到左緣，或按 [／Alt+M">'
        '<span class="sr-only">顯示目錄</span></button>'
        '<div class="navscrim" id="navscrim" hidden></div>'
    )


def nav_parts(prefix='', prev_url=None, next_url=None,
              prev_label=None, next_label=None, current_label=None,
              book_label=None, book_short=None, tools=False):
    """回傳 (preamble, sidebar)：preamble 是頂部列等，sidebar 在 .wrap 內。"""
    e = html.escape
    head = [topbar_html(prefix, current_label, book_label, book_short, tools)]
    parts = [
        '<nav id="sidebar" aria-label="全書目錄">',
        '<div class="navhead"><p class="brand"><a href="' + prefix + 'index.html">南山律典・白話對照</a></p>'
        '<button id="navclose" class="iconbtn" type="button" aria-label="關閉目錄">×</button>'
        '<button id="navcollapse" class="navcollapse" type="button" aria-label="收合目錄">⟨</button></div>',
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
             prev_label=None, next_label=None, current_label=None,
             book_label=None, book_short=None, tools=False):
    """相容用法：preamble ＋ sidebar。"""
    return ''.join(nav_parts(prefix, prev_url, next_url, prev_label, next_label,
                             current_label, book_label, book_short, tools))


def page(title, body, prefix='', prev_url=None, next_url=None,
         prev_label=None, next_label=None, current_label=None,
         extra_scripts=None, extra_head='', pager=False, tools=False,
         index_url=None, description=None, book_label=None, book_short=None,
         body_class=''):
    """完整 HTML 頁面。

    `body` 是 `<main>` 內容；卷末導覽與頁尾一律排在 `</main>` 之後，
    所以只替換 `<main>` 的生成器不會把它們吃掉。
    """
    e = html.escape
    nav_head, sidebar = nav_parts(prefix, prev_url, next_url, prev_label, next_label,
                                  current_label, book_label, book_short, tools)
    if pager:
        pager_s = pager_html(prev_url, next_url, prev_label, next_label,
                             index_url or (prefix + 'index.html'))
    else:
        pager_s = ''
    scripts = ['nav.js'] + list(extra_scripts or [])
    tags = ''.join('<script defer src="' + asset(prefix, s) + '"></script>' for s in scripts)
    desc = ('<meta name="description" content="' + e(description) + '">') if description else ''
    bc = (' class="%s"' % e(body_class)) if body_class else ''
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + e(title) + '｜南山律典・白話對照</title>'
        + desc +
        '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
        '<meta name="citation_author" content="UncleHandsome">'
        '<link rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">'
        '<link rel="stylesheet" href="' + asset(prefix, 'style.css') + '">'
        + _HEAD_SCRIPT + tags + extra_head + '</head><body' + bc + '>'
        + nav_head + '<div class="wrap">' + sidebar + '<div class="content">'
        + '<main id="main" tabindex="-1">' + body + '</main>'
        + pager_s + FOOTER.replace('ROOT', prefix)
        + '</div></div></body></html>'
    )
