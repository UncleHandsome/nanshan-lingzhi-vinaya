
# -*- coding: utf-8 -*-
import io, os, re, json, html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')

BOOKS = [
    dict(dir='01_行事鈔', out='xingshichao', title='四分律刪繁補闕行事鈔', by='唐·道宣律師　·　三大部之一'),
    dict(dir='02_戒疏', out='jieshu', title='四分律含注戒本疏', by='唐·道宣律師疏／宋·元照律師記　·　三大部之二'),
    dict(dir='03_業疏', out='yeshu', title='四分律刪補隨機羯磨疏', by='唐·道宣律師疏／宋·元照律師記　·　三大部之三', ju=True),
    dict(dir='資持記', srcdir='資持記_細分', out='zhichi', title='四分律行事鈔資持記', by='宋·元照律師　·　行事鈔之註'),
    dict(dir='04_比丘尼鈔', out='nicao', title='四分比丘尼鈔', by='唐·道宣律師　·　南山五大部之四', ju=True),
    dict(dir='05_拾毗尼義鈔', out='yichao', title='四分律拾毗尼義鈔', by='唐·道宣律師　·　南山五大部之五', ju=True),
]

def read_pairs(bookdir, srcdir=None, ju=False):
    if ju:
        import site_ju
        return [(v, [dict(o=o, t=t) for o, t in items]) for v, items in site_ju.get(bookdir)]
    S = os.path.join(B, 'TXT_分卷', srcdir or bookdir)
    T = os.path.join(B, 'AI語譯', 'out', bookdir)
    if not os.path.isdir(T): return []
    out = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]
        p = os.path.join(T, key + '.txt')
        if not os.path.exists(p): continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        juan = key.split('_', 1)[1] if '_' in key else '全'
        n = min(len(sp), len(tp))
        out.append((juan, [dict(o=sp[i], t=tp[i]) for i in range(n)]))
    return out

def vol_key(j):
    if j.startswith('卷首'): return '__PRE__'
    m = re.match(r'卷[上中下]', j)
    if m: return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j

FOOTER = ('<footer style="margin:3.5rem 0 0;padding-top:1.2rem;border-top:1px solid var(--line);'          'color:var(--fg2);font-size:12.5px;line-height:1.7">'
          '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯：本站自製。'
          '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權：'
          '姓名標示－非商業性－相同方式分享。轉載請保留出處，且不得作商業使用。'
          '<br><a href="ROOTLICENSE">授權全文</a></footer>')

EXTRA_CSS = """
/* 目錄頁：書籍卡片 */
main .card{border:1px solid var(--line);border-radius:8px;padding:1.1rem 1.2rem;margin:1.2rem 0 1.6rem;background:#fff}
main .card h2{margin:0 0 .2rem;border:0;padding:0;font-size:1.2rem}
main .card .byline{margin:0 0 .9rem;color:var(--fg2);font-size:13px}
main .card .grp{display:flex;flex-wrap:wrap;gap:.5rem}
main .card .grp a{display:inline-block;padding:.32rem .8rem;border:1px solid var(--line);border-radius:999px;
  text-decoration:none;color:var(--accent);font-size:14px;background:#faf8f2}
main .card .grp a:hover{background:#efeade;border-color:var(--accent2)}
main .intro{color:var(--fg2);font-size:14px;margin:0 0 1.4rem}

nav details.navj>summary{display:block;padding:.32rem 1rem;cursor:pointer;color:var(--fg);font-size:13px;font-weight:600}
nav details.navj>summary::-webkit-details-marker{display:none}
nav details.navj>summary:before{content:"▸ ";color:var(--accent2);font-size:10px}
nav details.navj[open]>summary:before{content:"▾ "}
nav a.book{padding-left:1rem;font-weight:600;color:var(--fg);font-size:13.5px}
nav .bklist .bk{margin:.15rem 0 .45rem}
nav .bklist details.navj{margin:.1rem 0}
nav .bklist details.navj>summary{display:block;padding:.34rem 1rem .18rem;cursor:pointer;color:var(--fg);font-size:13px;font-weight:600;line-height:1.45;list-style:none}
nav .bklist details.navj>summary::-webkit-details-marker{display:none}
nav .bklist details.navj>summary:before{content:"▸ ";color:var(--accent2);font-size:10px}
nav .bklist details.navj[open]>summary:before{content:"▾ "}
nav .bklist details.navj>summary.cur{color:var(--accent)}
nav .bklist details.navj ul{list-style:none;margin:0;padding:0 1rem .25rem 1.75rem}
nav .bklist details.navj li a{display:block;padding:.12rem 0;color:var(--fg2);font-size:13px;line-height:1.5;text-decoration:none}
nav .bklist details.navj li a:hover{color:var(--accent);text-decoration:underline}
nav .bklist details.navj li a.cur{color:var(--accent);font-weight:600}
nav .toclist a{display:block;padding:.12rem 1rem;color:var(--fg2);font-size:13px;line-height:1.5;text-decoration:none}
nav .toclist a:hover{color:var(--accent);text-decoration:underline}
main h1{margin-bottom:.4rem}
.byline{color:var(--fg2);font-size:13px;margin:0 0 1.4rem}
.pair{margin:1.15rem 0;padding-bottom:.9rem;border-bottom:1px dotted var(--line)}
.pair .o{background:#f4efe2;border-left:3px solid #cdbc9c;padding:.45rem .8rem;color:#5d4c3a;
  font-size:15.5px;line-height:1.75;border-radius:0 4px 4px 0}
.pair .t{margin:.45rem 0 0;font-size:17px;line-height:1.95;text-align:justify}
.pager{display:flex;justify-content:space-between;margin:2.5rem 0 0;font-size:14px}
mark{background:#ffe9a8;padding:0 .08em;border-radius:2px}
#hits .hit{border-bottom:1px solid var(--line);padding:.8rem 0}
#hits .meta{color:var(--fg2);font-size:12.5px;margin-bottom:.2rem}
#hits .o{color:#5d4c3a;font-size:14px}
#hits .t{font-size:15.5px}
@media(max-width:820px){nav{display:none}main{padding:1.4rem}}
"""

import toc_rules as TR


def toc_match(book, text):
    return TR.match(book, text)


def toc_label(book, text):
    return TR.label(book, text)


def toc_whole_line(book, text):
    return TR.is_line(book, text)


VOL_ORDER = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
             '卷中之一', '卷中之二', '卷中之三', '卷中之四',
             '卷下之一', '卷下之二', '卷下之三', '卷下之四',
             '卷上', '卷中', '卷下', '卷一', '卷二', '卷三', '卷四',
             '上一上', '上一下', '上二', '上三', '上四',
             '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
             '下一', '下二', '下三', '下四']


def vol_order_key(v):
    try:
        return VOL_ORDER.index(v)
    except ValueError:
        return 999



def read_hb_toc():
    import glob as _g
    t = {}
    for f in _g.glob(os.path.join(SITE, 'hebian', '*.html')):
        v = os.path.basename(f)[:-5]
        h = io.open(f, encoding='utf-8').read()
        items, seen = [], set()
        for m in re.finditer(r'<h2 class="sec" id="p(\d+)">([^<]+)</h2>', h):
            sid = int(m.group(1))
            if sid in seen:
                continue
            seen.add(sid)
            items.append((sid, m.group(2)))
        t[v] = items
    return t


HB_TOC = read_hb_toc()


def nav_html(cur_book=None, prefix='', toc=None, prev=None, nxt=None):
    parts = ['<nav><h1><a href="INDEX">南山律典・白話對照</a></h1>']
    parts.append('<div class="grp"><b>全書</b><a href="INDEX">目錄</a><a href="SEARCH">全文搜尋</a>'
                 '<a href="APPENDIX">附錄</a><a href="UNTRANSLATED">未譯清單</a></div>')
    if (prev or nxt) and cur_book:
        parts.append('<div class="grp"><b>分卷</b>')
        if prev:
            parts.append('<a href="' + prefix + cur_book['out'] + '/' + prev + '.html">← ' + html.escape(prev) + '</a>')
        if nxt:
            parts.append('<a href="' + prefix + cur_book['out'] + '/' + nxt + '.html">' + html.escape(nxt) + ' →</a>')
        parts.append('</div>')
    parts.append('<div class="grp"><b>書目</b><div class="tree" id="navtree" data-root="' + prefix + '">'
                 '<noscript><a href="' + prefix + 'index.html">目錄</a></noscript></div></div></nav>')
    return ''.join(parts)


def page(title, body, cur_book=None, prefix='', toc=None, prev=None, nxt=None):
    nav = (nav_html(cur_book, prefix, toc, prev, nxt)
           .replace('INDEX', prefix + 'index.html')
           .replace('SEARCH', prefix + 'search.html')
           .replace('APPENDIX', prefix + 'appendix.html')
           .replace('UNTRANSLATED', prefix + 'untranslated.html'))
    css = prefix + 'style.css?v=10'
    return ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + '｜南山律典・白話對照</title>'
            '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
            '<meta name="citation_author" content="UncleHandsome">'
            '<link rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">'
            '<link rel="stylesheet" href="' + css + '"><script defer src="' + prefix + 'nav.js?v=6"></script></head><body><div class="wrap">'
            + nav + '<main>' + body + FOOTER.replace('ROOT', prefix) + '</main></div></body></html>')

def build():
    os.makedirs(SITE, exist_ok=True)
    css_path = os.path.join(SITE, 'style.css')
    base_css = io.open(css_path, encoding='utf-8').read() if os.path.exists(css_path) else ''
    if 'details.navj>summary.cur' not in base_css:
        io.open(css_path, 'w', encoding='utf-8').write(base_css + '\n' + EXTRA_CSS)
    all_books = []
    for bk in BOOKS:
        pairs = read_pairs(bk['dir'], bk.get('srcdir'), bk.get('ju'))
        if not pairs: continue
        groups = {}
        for j, items in pairs:
            groups.setdefault(vol_key(j), []).extend(items)
        if '__PRE__' in groups:
            pre = groups.pop('__PRE__')
            first = list(groups.keys())[0] if groups else '卷一'
            groups[first] = pre + groups.get(first, [])
        bk['_vols'] = [(v, '') for v in sorted(groups, key=vol_order_key)]
        bk['_groups'] = groups
        all_books.append(bk)
    # 預先計算每卷篇目（供側欄三層樹）
    for bk in all_books:
        tmap = {}
        for v, items in bk['_groups'].items():
            tt = []
            run, drop = [], set()
            for i2, it2 in enumerate(items):
                if TR.match('xingshichao', it2['o'].strip()):
                    run.append(i2)
                else:
                    if len(run) >= 3:
                        drop.update(run)
                    run = []
            if len(run) >= 3:
                drop.update(run)
            drop_toc = set()
            run3 = []
            for i2, it2 in enumerate(items[:40]):
                o2 = it2['o'].strip()
                if toc_match(bk['out'], o2) and len(re.sub(r'[^\u4e00-\u9fff]', '', o2)) <= 10:
                    run3.append(i2)
                else:
                    if len(run3) >= 3:
                        drop_toc.update(run3)
                    run3 = []
            if len(run3) >= 3:
                drop_toc.update(run3)
            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                if re.match(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$', o):
                    continue
                if o.startswith('【目錄】') or o.startswith('【條目】'):
                    pass
                elif i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if bk['out'] == 'yeshu' and _lb not in {'集法緣成篇第一','諸界結解篇第二','諸戒受法篇第三','衣藥受淨篇第四','諸說戒法篇第五','諸眾安居法篇第六','諸眾自恣法篇第七','諸分衣法篇第八','懺六聚法篇第九','雜法住持篇第十'}:
                        _lb = ''
                    if _lb and _lb not in [n for _, n in tt]:
                        tt.append((len(tt) + 1, _lb))
            tmap[v] = tt
        bk['_toc'] = tmap
    search_idx = {}
    for bk in all_books:
        outdir = os.path.join(SITE, bk['out']); os.makedirs(outdir, exist_ok=True)
        vols = list(bk['_groups'].keys())
        entries = []
        for i, v in enumerate(vols):
            items = bk['_groups'][v]
            body = ['<h1>' + html.escape(bk['title']) + '　' + html.escape(v) + '</h1>',
                    '<p class="byline">' + html.escape(bk['by']) + '　｜　白話對照</p>']
            toc = []
            # 偵測「連續篇名」的卷首目次，整段略過（側欄已有篇目）
            drop = set()
            run = []
            for i2, it2 in enumerate(items):
                if TR.match('xingshichao', it2['o'].strip()):
                    run.append(i2)
                else:
                    if len(run) >= 3:
                        drop.update(run)
                    run = []
            if len(run) >= 3:
                drop.update(run)
            drop_toc = set()
            run3 = []
            for i2, it2 in enumerate(items[:40]):
                o2 = it2['o'].strip()
                if toc_match(bk['out'], o2) and len(re.sub(r'[^\u4e00-\u9fff]', '', o2)) <= 10:
                    run3.append(i2)
                else:
                    if len(run3) >= 3:
                        drop_toc.update(run3)
                    run3 = []
            if len(run3) >= 3:
                drop_toc.update(run3)
            for i2, it in enumerate(items):
                if i2 in drop:
                    continue
                o = it['o'].strip()
                # 略過卷首「1 X篇(上一)」這種重複的目次序號行
                if re.match(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$', o):
                    continue
                # 篇名行改成標題，不再重複成 pair
                if TR.match('xingshichao', o):
                    sid = len(toc) + 1
                    toc.append((sid, o))
                    body.append('<h2 class="sec" id="p%d">%s</h2>' % (sid, html.escape(o)))
                    continue
                sid_s = 's' + str(len(body))
                it['_id'] = sid_s
                if o.startswith('【目錄】') or o.startswith('【條目】'):
                    pass
                elif i2 not in drop_toc and toc_match(bk['out'], o):
                    _lb = toc_label(bk['out'], o)
                    if _lb.startswith('序文：'):
                        _lb = '序文'
                    if bk['out'] == 'jieshu' and v in ('卷一', '卷一上') and _lb not in ('序文', '凡例', '目錄', '條目'):
                        _lb = ''
                    if bk['out'] == 'yeshu' and _lb not in {'集法緣成篇第一','諸界結解篇第二','諸戒受法篇第三','衣藥受淨篇第四','諸說戒法篇第五','諸眾安居法篇第六','諸眾自恣法篇第七','諸分衣法篇第八','懺六聚法篇第九','雜法住持篇第十'}:
                        _lb = ''
                    if _lb and _lb not in [n for _, n in toc]:
                        sid = len(toc) + 1
                        toc.append((sid, _lb))
                        it['_id'] = 'p' + str(sid)
                        body.append('<h2 class="sec" id="p' + str(sid) + '">' + html.escape(_lb) + '</h2>')
                        # 這一段本身就是篇名（整行相同）→ 只留標題，不再重複成 pair
                        _o2 = re.sub(r'^【[律註疏記]】\s*', '', o).rstrip('。')
                        if re.sub(r'[^\u4e00-\u9fff]', '', _o2) == re.sub(r'[^\u4e00-\u9fff]', '', _lb):
                            continue
                _oc = ''
                if it['o'].startswith('【記】'):
                    _oc = ' ji'
                elif it['o'].startswith('【疏】'):
                    _oc = ' shu'
                body.append('<div class="pair" id="' + sid_s + '"><div class="o' + _oc + '">' + html.escape(it['o']) + '</div>'
                            + '<div class="t">' + html.escape(it['t']) + '</div></div>')
            prev = vols[i-1] if i > 0 else None
            nxt = vols[i+1] if i+1 < len(vols) else None
            bk['_curvol'] = v
            pager = ['<div class="pager">']
            pager.append('<a href="' + (prev + '.html') + '">← ' + html.escape(prev) + '</a>' if prev else '<span></span>')
            pager.append('<a href="' + (nxt + '.html') + '">' + html.escape(nxt) + ' →</a>' if nxt else '<span></span>')
            pager.append('</div>')
            body += pager
            io.open(os.path.join(outdir, v + '.html'), 'w', encoding='utf-8').write(
                page(bk['title'] + '　' + v, ''.join(body), bk, '../', toc, prev, nxt))
            for it in items:
                entries.append(dict(v=v, o=it['o'], t=it['t'], i=it.get('_id', '')))
        search_idx[bk['out']] = dict(title=bk['title'], entries=entries)
    # 搜尋索引（每本一檔）
    os.makedirs(os.path.join(SITE, 'search'), exist_ok=True)
    for out, data in search_idx.items():
        io.open(os.path.join(SITE, 'search', out + '.js'), 'w', encoding='utf-8').write('window.SIDX=window.SIDX||{};window.SIDX["' + out + '"]=' + json.dumps(data, ensure_ascii=False) + ';')
    # 目錄
    cards = []
    for bk in all_books:
        links = ''.join('<a href="' + bk['out'] + '/' + v + '.html">' + html.escape(v) + '</a>' for v in bk['_groups'])
        cards.append('<section class="card"><h2>' + html.escape(bk['title']) + '</h2>'
                     + '<p class="byline">' + html.escape(bk['by']) + '　·　' + str(len(bk['_groups'])) + ' 卷</p>'
                     + '<div class="grp">' + links + '</div></section>')
    idx_body = ('<h1>南山律典・白話對照</h1>'
                '<section class="card"><h2>行事鈔資持記・句級合編</h2><p class="byline">鈔文與記文逐段並列　·　12 卷</p><div class="grp"><a href="hebian/卷上之一.html">卷上之一</a><a href="hebian/卷上之二.html">卷上之二</a><a href="hebian/卷上之三.html">卷上之三</a><a href="hebian/卷上之四.html">卷上之四</a><a href="hebian/卷中之一.html">卷中之一</a><a href="hebian/卷中之二.html">卷中之二</a><a href="hebian/卷中之三.html">卷中之三</a><a href="hebian/卷中之四.html">卷中之四</a><a href="hebian/卷下之一.html">卷下之一</a><a href="hebian/卷下之二.html">卷下之二</a><a href="hebian/卷下之三.html">卷下之三</a><a href="hebian/卷下之四.html">卷下之四</a></div></section>' + '<p class="intro">道宣律師三大部與相關鈔疏的白話對照本，逐段原文與白話並列；原文採 CBETA 電子佛典（大正藏／卍續藏）。</p>' + '<p class="intro"><a href="appendix.html">附錄：名相與度量衡</a></p>'
                + ''.join(cards) + '<p class="byline"><a href="search.html">→ 全文搜尋</a></p>')
    io.open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page('目錄', idx_body))
    # 搜尋頁
    sb = ('<h1>全文搜尋</h1>'
          '<div class="searchbox"><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" autocomplete="off" autofocus>'
          '<kbd>/</kbd></div>'
          '<p class="byline">可用 ↑↓ 選擇結果、Enter 開啟；結果依原文起始、卷名、白話加權排序。</p>'
          '<p class="byline" id="count"></p><div id="hits"></div>'
          '<script>' + SEARCH_JS + '</script>')
    io.open(os.path.join(SITE, 'search.html'), 'w', encoding='utf-8').write(page('搜尋', sb))
    # 側欄資料
    nav_books = []
    for bk in all_books:
        vols = []
        for v, _u in bk['_vols']:
            secs = [[('p%d' % sid), nm] for sid, nm in (bk['_toc'].get(v) or [])]
            vols.append(dict(v=v, secs=secs))
        nav_books.append(dict(out=bk['out'], title=bk['title'], vols=vols))
    try:
        import glob as _g
        hbv = []
        for f in sorted(_g.glob(os.path.join(SITE, 'hebian', '*.html'))):
            v = os.path.basename(f)[:-5]
            h2s = re.findall(r'<h2 class="sec" id="(p\d+)">([^<]+)</h2>', io.open(f, encoding='utf-8').read())
            hbv.append(dict(v=v, secs=[[a, b] for a, b in dict.fromkeys(h2s)]))
        if hbv:
            nav_books.append(dict(out='hebian', title='行事鈔資持記・句級合編', vols=hbv))
    except Exception as _e:
        print('hb nav', _e)
    io.open(os.path.join(SITE, 'nav.json'), 'w', encoding='utf-8').write(
        json.dumps(dict(books=nav_books), ensure_ascii=False))
    import shutil as _sh
    _sh.copyfile(os.path.join(B, '_src', 'nav.js'), os.path.join(SITE, 'nav.js'))
    print('nav.json', len(nav_books), 'books')

    # 未譯段落清單頁（目前 0 段）
    try:
        import json as _json
        rows = _json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'untranslated.json'), encoding='utf-8'))
        nseg = sum(len(b['rows']) for b in rows)
    except Exception:
        nseg = 0
    ub = ['<h1>未譯段落清單</h1>',
          '<p class="byline">全書逐段比對「原文／白話」的結果</p>',
          '<div class="intro"><p>目前未譯段落：<b>%d</b> 段。</p>' % nseg]
    if nseg == 0:
        ub.append('<p>六部書（行事鈔、戒疏、業疏、資持記、尼鈔、尼義鈔）與句級合編，'
                  '每一段原文都已有對應白話，沒有「直接照抄原文」的段落。</p>')
    ub.append('<p>同名 PDF（<code>白話/未譯段落清單.pdf</code>）另行提供。</p></div>')
    io.open(os.path.join(SITE, 'untranslated.html'), 'w', encoding='utf-8').write(
        page('未譯段落清單', ''.join(ub)))
    print('untranslated page, segs', nseg)
    print('books', len(all_books), 'vols', sum(len(b['_groups']) for b in all_books))

SEARCH_JS = """
var BOOKS=[['xingshichao','四分律刪繁補闕行事鈔'],['yeshu','四分律刪補隨機羯磨疏'],['jieshu','四分律含注戒本疏'],['zhichi','四分律行事鈔資持記'],['nicao','四分比丘尼鈔'],['yichao','四分律拾毗尼義鈔'],['hebian','行事鈔資持記・句級合編']];
var loaded={}, ACTIVE=-1;
function loadBook(id){ if(loaded[id]) return Promise.resolve(loaded[id]);
  return new Promise(function(res){ var s=document.createElement('script'); s.src='search/'+id+'.js';
    s.onload=function(){ loaded[id]=window.SIDX[id]; res(loaded[id]); }; s.onerror=function(){ res({entries:[]}); }; document.head.appendChild(s); }); }
function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function escq(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
function hl(s,q){ if(!q) return esc(s); var re=new RegExp('('+escq(q)+')','gi');
  return esc(s).replace(re,'<mark>$1</mark>'); }
function snip(s,q,n){ if(!q) return esc(s.slice(0,n));
  var i=s.toLowerCase().indexOf(q.toLowerCase()); if(i<0) return esc(s.slice(0,n));
  var a=Math.max(0,i-30), b=Math.min(s.length,i+q.length+70);
  return (a>0?'…':'')+hl(s.slice(a,b),q)+(b<s.length?'…':''); }
function score(e,q){ var s=0; if(e.o.indexOf(q)===0) s+=6; if(e.o.indexOf(q)>=0) s+=3;
  if(e.t.indexOf(q)>=0) s+=2; if((e.v||'').indexOf(q)>=0) s+=4; return s; }
async function run(q){
  var c=document.getElementById('count'), h=document.getElementById('hits');
  if(!q){ c.textContent=''; h.innerHTML=''; return; }
  c.textContent='搜尋中…'; var t0=Date.now(); var out=[];
  for(var i=0;i<BOOKS.length;i++){
    var b=await loadBook(BOOKS[i][0]); var es=(b&&b.entries)||[];
    for(var j=0;j<es.length;j++){ var e=es[j];
      if(e.o.indexOf(q)>=0||e.t.indexOf(q)>=0){
        out.push({book:BOOKS[i][1],bid:BOOKS[i][0],v:e.v,o:e.o,t:e.t,i:e.i||'',sc:score(e,q)});
      }
    }
  }
  out.sort(function(a,b){ return b.sc-a.sc; });
  var total=out.length; out=out.slice(0,300);
  c.textContent = total? ('找到 '+total+' 筆'+(total>300?'（顯示前 300 筆）':'')+'　·　'+(Date.now()-t0)+' ms') : '沒有結果';
  if(!total){
    h.innerHTML='<div class="empty">查無「'+esc(q)+'」。可試：<a href="?q=羯磨">羯磨</a>、<a href="?q=波羅夷">波羅夷</a>、<a href="?q=安居">安居</a>，或較短的關鍵字。</div>';
    return;
  }
  var parts=[], lastBook='';
  for(var k=0;k<out.length;k++){ var x=out[k];
    if(x.book!==lastBook){ parts.push('<h3 class="hitbook">'+esc(x.book)+'</h3>'); lastBook=x.book; }
    parts.push('<div class="hit" data-idx="'+k+'"><div class="meta">'+esc(x.v)
      +'　<a href="'+x.bid+'/'+x.v+'.html'+(x.i?'#'+x.i:'')+'">前往 →</a></div>'
      +'<div class="o">'+snip(x.o,q,110)+'</div><div class="t">'+snip(x.t,q,110)+'</div></div>');
  }
  h.innerHTML=parts.join('');
  ACTIVE=-1;
}
function setActive(i){
  var hs=document.querySelectorAll('#hits .hit'); if(!hs.length) return;
  if(ACTIVE>=0&&hs[ACTIVE]) hs[ACTIVE].classList.remove('active');
  ACTIVE=(i+hs.length)%hs.length; hs[ACTIVE].classList.add('active');
  hs[ACTIVE].scrollIntoView({block:'nearest'});
}
document.addEventListener('DOMContentLoaded',function(){
  var inp=document.getElementById('q'); if(!inp) return; var t;
  var m=(location.search.match(/[?&]q=([^&]*)/)||[]); if(m[1]){ inp.value=decodeURIComponent(m[1].replace(/\+/g,' ')); run(inp.value.trim()); }
  inp.addEventListener('input',function(e){ clearTimeout(t); t=setTimeout(function(){
    var q=e.target.value.trim();
    if(history.replaceState) history.replaceState(null,'', q?('?q='+encodeURIComponent(q)):'search.html');
    run(q); },200); });
  inp.addEventListener('keydown',function(e){
    if(e.key==='ArrowDown'){ e.preventDefault(); setActive(ACTIVE+1); }
    else if(e.key==='ArrowUp'){ e.preventDefault(); setActive(ACTIVE-1); }
    else if(e.key==='Enter'){ var a=document.querySelector('#hits .hit.active a'); if(a) location.href=a.href; }
    else if(e.key==='Escape'){ inp.value=''; run(''); }
  });
  document.addEventListener('keydown',function(e){
    if(e.target&&/input|textarea|select/i.test(e.target.tagName)) return;
    if(e.key==='/'){ e.preventDefault(); inp.focus(); }
  });
});
"""

build()
