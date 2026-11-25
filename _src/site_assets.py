# -*- coding: utf-8 -*-
"""全站共用頁面骨架、導覽與資源版本。

這個模組只負責產生字串，不讀寫檔案，讓 site2.py / site_hebian.py 都能安全 import。

2026-11-23 PDF reader 式版面（v27）
-----------------------------------
* 全站共用同一個 sticky 頂部列：`☰ 目錄` → 分卷導覽（← 上一卷／目前卷／下一卷 →）
  → 書名・卷 → 全域搜尋 → 常駐閱讀工具。
* 閱讀工具不再收成「閱讀工具」按鈕＋下拉面板；工具列直接顯示在頂部列。
* 側欄只留書目與卷／篇 TOC，不再有「分卷」群組或全書連結列。
* 桌面側欄預設展開；窄螢幕自動變抽屜，抽屜頂端對齊實際頂部列高度。
"""
import html

ASSET_VERSION = '69'

BOOK_OPTIONS = [
    ('行事鈔', 'xingshichao/卷上.html'),
    ('戒疏', 'jieshu/卷一.html'),
    ('業疏', 'yeshu/卷一.html'),
    ('資持記', 'zhichi/上一上.html'),
    ('尼鈔', 'nicao/卷上.html'),
    ('義鈔', 'yichao/卷上.html'),
    ('合編', 'hebian/卷上之一.html'),
]

FOOTER = (
    '<footer class="sitefoot">'
    '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯：本站自製。'
    '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權：'
    '姓名標示－非商業性－相同方式分享。轉載請保留出處，且不得作商業使用。'
    '<br><a href="ROOTLICENSE">授權全文</a></footer>'
)

_HEAD_SCRIPT = (
    '<script>try{var h=document.documentElement;'
    # 原文／白話各自獨立開關（dsh-show-o / dsh-show-t；舊 dsh-read-mode 自動換算）
    'var o=localStorage.getItem("dsh-show-o"),t=localStorage.getItem("dsh-show-t");'
    'if(o===null&&t===null){var m=localStorage.getItem("dsh-read-mode")||"";'
    'if(m==="o"){o="1";t="0";}else if(m==="t"){o="0";t="1";}}'
    'if(o==="0")h.classList.add("hide-o");'
    'if(t==="0")h.classList.add("hide-t");'
    'var tw=localStorage.getItem("dsh-twocol");'
    'if(tw!=="0" && (!window.matchMedia || window.matchMedia("(min-width: 1200px)").matches))h.classList.add("twocol");'
    'var f=parseInt(localStorage.getItem("dsh-fs")||"100",10);'
    'if(f>=80&&f<=170){document.documentElement.style.setProperty("--fs",(18*f/100).toFixed(1)+"px");}'
    '}catch(e){}</script>'
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


def pager_html(prev_url, next_url, prev_label, next_label, index_url,
               aria_label='卷導覽'):
    """卷末／篇末導覽：`<nav>` landmark，首末卷（篇）允許單邊。

    卷目錄頁用預設「卷導覽」；篇頁用「篇導覽」（whole-book 篇序 prev/next）。
    """
    e = html.escape
    parts = ['<nav class="pager" aria-label="' + e(aria_label) + '">']
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
    """常駐頂部列閱讀工具：顯示模式、雙欄對照、複製本段連結。

    不再有「閱讀工具」按鈕／下拉面板；工具列由頁面骨架直接輸出並一直可見。
    """
    return (
        '<div class="tb-readtools toolpanel readtools" id="toolpanel" role="group" aria-label="閱讀設定">'
        '<span class="tb-seg tb-showseg" role="group" aria-label="顯示欄位">'
        '<button type="button" data-show="o" aria-pressed="true" title="顯示／隱藏原文">原文</button>'
        '<button type="button" data-show="t" aria-pressed="true" title="顯示／隱藏白話">白話</button>'
        '</span>'
        '<button type="button" data-twocol-toggle aria-pressed="false" title="原文與白話左右並排，需寬螢幕">並排</button>'
        '<button type="button" data-copy-anchor title="複製目前段落的網址">複製</button>'
        '<span class="tb-seg tb-fsseg" role="group" aria-label="字級">'
        '<button type="button" data-fs="dec" title="縮小字級">A－</button>'
        '<button type="button" data-fs="reset" title="重設字級">100%</button>'
        '<button type="button" data-fs="inc" title="放大字級">A＋</button>'
        '</span>'
        '<span class="tb-seg tb-labelseg" role="group" aria-label="隱藏段別">'
        '<button type="button" data-hide-label="j" aria-pressed="false" title="隱藏記文">記文</button>'
        '<button type="button" data-hide-label="z" aria-pressed="false" title="隱藏註文">註文</button>'
        '<button type="button" data-hide-label="lv" aria-pressed="false" title="隱藏律文">律文</button>'
        '<button type="button" data-hide-label="x" aria-pressed="false" title="隱藏序文">序文</button>'
        '<button type="button" data-hide-label="s" aria-pressed="false" title="隱藏疏文">疏文</button>'
        '<button type="button" data-hide-label="c" aria-pressed="false" title="隱藏鈔文">鈔文</button>'
        '</span>'
        '</div>'
    )


def volnav_html(prev_url=None, next_url=None, prev_label=None,
                next_label=None, current_label=None):
    """頂部列分卷導覽：← 上一卷／目前卷／下一卷 →；首末卷單邊隱藏。"""
    if not current_label or not (prev_url or next_url):
        return ''
    e = html.escape
    parts = ['<nav class="tb-volnav" aria-label="分卷導覽">']
    if prev_url:
        lab = prev_label or '上一卷'
        parts.append('<a class="tb-vol tb-volprev" rel="prev" href="' + prev_url + '" '
                     'title="上一卷：' + e(lab) + '">'
                     '<span class="tb-vol-arrow" aria-hidden="true">←</span>'
                     '<span class="tb-vol-name">' + e(lab) + '</span></a>')
    parts.append('<span class="tb-volcur" aria-current="page">' + e(current_label) + '</span>')
    if next_url:
        lab = next_label or '下一卷'
        parts.append('<a class="tb-vol tb-volnext" rel="next" href="' + next_url + '" '
                     'title="下一卷：' + e(lab) + '">'
                     '<span class="tb-vol-name">' + e(lab) + '</span>'
                     '<span class="tb-vol-arrow" aria-hidden="true">→</span></a>')
    parts.append('</nav>')
    return ''.join(parts)


def topbar_html(prefix='', current_label=None, book_label=None, book_short=None,
                tools=False, prev_url=None, next_url=None,
                prev_label=None, next_label=None):
    """全站共用頂部列（單列）：固定骨架

    ☰ 目錄｜⌂ 首頁｜書目切換｜南山律典｜分卷導覽｜目前位置｜……｜
    閱讀工具｜下載｜搜尋框＋搜尋鈕

    幾何固定：書目切換在首頁鈕之後；品牌名固定在書目切換與分卷導覽之間
    （v63：不隨分卷寬度跳動）；下載、搜尋框固定在右緣（閱讀工具在它們
    左側，寬度由 crumb 吸收），首頁／搜尋頁／內文頁位置一致。
    書目切換在首頁／搜尋頁顯示「選書…」，選了直接進該書第一卷。
    """
    e = html.escape
    shorts = dict(BOOK_OPTIONS)
    real = book_short in shorts
    opts = []
    if not real:
        opts.append('<option value="" selected>選書…</option>')
    for short, href in BOOK_OPTIONS:
        opts.append('<option value="%s"%s>%s</option>'
                    % (prefix + href,
                       ' selected' if real and short == book_short else '', short))
    title_attr = (' title="%s"' % e(book_label)) if book_label else ''
    booksel = ('<div class="tb-bookslot">'
               '<select id="tb-bookpick" class="tb-bookselect" aria-label="切換書目"'
               + title_attr + '>' + ''.join(opts) + '</select></div>')

    vol = volnav_html(prev_url, next_url, prev_label, next_label, current_label)
    # v63：品牌名固定在「書目切換」之後、「分卷導覽」之前。
    # 分卷導覽寬度隨頁面變動，品牌若放在 crumb 內會左右跳。
    brand = ('<a class="tb-brand" href="' + prefix + 'index.html" '
             'title="南山律典：回首頁">南山律典</a>')
    crumb = []
    # 有分卷導覽時，目前卷已經顯示在分卷區；沒有分卷時（首頁／搜尋／下載等）
    # 顯示目前位置。內文頁的「目前篇名」由 ui.js 接在 crumb 後面。
    if current_label and not vol:
        crumb.append('<span class="tb-where">' + e(current_label) + '</span>')

    search = (
        '<form class="tb-searchform" action="' + prefix + 'search.html" method="get" role="search">'
        '<input id="tbq" name="q" type="search" placeholder="搜尋…" autocomplete="off" '
        'aria-label="全站全文搜尋" title="輸入關鍵字後按 Enter（Ctrl/⌘ K）">'
        '<button class="tb-searchgo" type="submit" title="送出搜尋">搜尋</button>'
        '</form>'
        '<a class="tb-btn tb-searchbtn" href="' + prefix + 'search.html" '
        'aria-label="全文搜尋" title="全文搜尋（Ctrl/⌘ K）">搜尋</a>'
    )

    bars = (
        '<header class="topbar">'
        '<button id="navtoggle" class="tb-btn tb-menu" type="button" aria-controls="sidebar" '
        'aria-expanded="true" aria-label="開合目錄" title="開合目錄（[ 或 Alt+M）">'
        '<span class="tb-ico" aria-hidden="true">☰</span><span class="tb-menulabel">目錄</span></button>'
        '<a class="tb-btn tb-gohome" href="' + prefix + 'index.html" aria-label="回到首頁" title="回到首頁">'
        '<span class="tb-homeicon" aria-hidden="true">⌂</span><span class="tb-homelabel">首頁</span></a>'
        + booksel
        + brand
        + vol
        + '<div class="tb-crumb">' + ''.join(crumb) + '</div>'
        '<div class="tb-right">'
        + (tools_html() if tools else '')
        + search
        + '<a class="tb-btn tb-dl" href="' + prefix + 'download.html" '
        'title="下載 Word／PDF 對照本" aria-label="下載 Word 與 PDF">下載</a></div>'
        '</header>'
    )
    return (
        '<a class="skip-link" href="#main">跳至正文</a>'
        + bars
        + '<button id="edgepeek" class="edgepeek" type="button" aria-controls="sidebar" '
        'aria-label="顯示目錄" title="顯示目錄：滑鼠移到左緣，或按 [／Alt+M；'
        '展開後可按側欄「📌 固定」">'
        '<span class="sr-only">顯示目錄</span></button>'
        '<div class="navscrim" id="navscrim" hidden></div>'
    )


def nav_parts(prefix='', prev_url=None, next_url=None,
              prev_label=None, next_label=None, current_label=None,
              book_label=None, book_short=None, tools=False):
    """回傳 (preamble, sidebar)：preamble 是頂部列等，sidebar 在 .wrap 內。

    側欄只放書目與卷／篇 TOC；分卷與全書連結不再出現在側欄。
    """
    head = [topbar_html(prefix, current_label, book_label, book_short, tools,
                        prev_url, next_url, prev_label, next_label)]
    parts = [
        '<nav id="sidebar" aria-label="全書目錄">',
        '<div class="navhead"><p class="brand"><a href="' + prefix + 'index.html">南山律典・白話對照</a></p>'
        '<button id="navpin" class="navpin" type="button" aria-label="固定目錄" '
        'title="固定目錄：不再自動收起">📌 固定</button>'
        '<button id="navclose" class="iconbtn" type="button" aria-label="關閉目錄">×</button>'
        '<button id="navcollapse" class="navcollapse" type="button" aria-label="收合目錄">⟨</button></div>',
        '<div id="navtree" data-root="' + prefix + '" '
        'data-nav-version="' + ASSET_VERSION + '">'
        '<noscript><a href="' + prefix + 'index.html">目錄</a></noscript></div>',
        '</nav>',
    ]
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
    scripts = ['nav.js', 'ui.js'] + list(extra_scripts or [])
    tags = ''.join('<script defer src="' + asset(prefix, s) + '"></script>' for s in scripts)
    desc = ('<meta name="description" content="' + e(description) + '">') if description else ''
    classes = [c for c in (body_class, 'page-reader' if tools else '') if c]
    bc = (' class="%s"' % e(' '.join(classes))) if classes else ''
    return (
        '<!doctype html><html lang="zh-Hant">'
        '<head><meta charset="utf-8">'
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
