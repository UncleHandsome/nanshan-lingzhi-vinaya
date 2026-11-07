
# -*- coding: utf-8 -*-
import io, os, re, json, html, shutil

import site_assets as SA

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




def page(title, body, cur_book=None, prefix='', toc=None, prev=None, nxt=None,
         extra_scripts=None, extra_head=''):
    prev_url = next_url = None
    prev_label = next_label = None
    if cur_book and prev:
        prev_url = prefix + cur_book['out'] + '/' + prev + '.html'
        prev_label = prev
    if cur_book and nxt:
        next_url = prefix + cur_book['out'] + '/' + nxt + '.html'
        next_label = nxt
    current_label = cur_book.get('_curvol') if cur_book else None
    return SA.page(title, body, prefix=prefix, prev_url=prev_url, next_url=next_url,
                   prev_label=prev_label, next_label=next_label,
                   current_label=current_label, extra_scripts=extra_scripts,
                   extra_head=extra_head)


def build():
    os.makedirs(SITE, exist_ok=True)
    shutil.copyfile(os.path.join(B, '_src', 'site.css'), os.path.join(SITE, 'style.css'))
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
    # 搜尋 manifest：書名／索引檔由建置端統一產生，search.js 不再硬編碼
    search_books = [dict(id=bk['out'], title=bk['title'], file='search/' + bk['out'] + '.js') for bk in all_books]
    if os.path.exists(os.path.join(SITE, 'search', 'hebian.js')):
        search_books.append(dict(id='hebian', title='行事鈔資持記・句級合編', file='search/hebian.js'))
    io.open(os.path.join(SITE, 'search', 'manifest.js'), 'w', encoding='utf-8').write(
        'window.SEARCH_BOOKS=' + json.dumps(search_books, ensure_ascii=False) + ';')
    shutil.copyfile(os.path.join(B, '_src', 'search.js'), os.path.join(SITE, 'search.js'))
    # 目錄
    cards = []
    for bk in all_books:
        links = ''.join('<a href="' + bk['out'] + '/' + v + '.html">' + html.escape(v) + '</a>' for v in bk['_groups'])
        cards.append('<section class="card"><h2>' + html.escape(bk['title']) + '</h2>'
                     + '<p class="byline">' + html.escape(bk['by']) + '　·　' + str(len(bk['_groups'])) + ' 卷</p>'
                     + '<div class="grp">' + links + '</div></section>')
    idx_body = ('<h1>南山律典・白話對照</h1>'
                '<form class="homefind" action="search.html" method="get" role="search">'
                '<input type="search" name="q" placeholder="搜尋全站：羯磨、波羅夷、安居…" aria-label="全文搜尋">'
                '<button type="submit">全文搜尋</button></form>'
                '<p class="hint">站內全文：<code>Ctrl/⌘ K</code>；瀏覽器尋找仍用 <code>Ctrl/⌘ F</code>。</p>'
                '<section class="card"><h2>行事鈔資持記・句級合編</h2><p class="byline">鈔文與記文逐段並列　·　12 卷</p><div class="grp"><a href="hebian/卷上之一.html">卷上之一</a><a href="hebian/卷上之二.html">卷上之二</a><a href="hebian/卷上之三.html">卷上之三</a><a href="hebian/卷上之四.html">卷上之四</a><a href="hebian/卷中之一.html">卷中之一</a><a href="hebian/卷中之二.html">卷中之二</a><a href="hebian/卷中之三.html">卷中之三</a><a href="hebian/卷中之四.html">卷中之四</a><a href="hebian/卷下之一.html">卷下之一</a><a href="hebian/卷下之二.html">卷下之二</a><a href="hebian/卷下之三.html">卷下之三</a><a href="hebian/卷下之四.html">卷下之四</a></div></section>' + '<p class="intro">道宣律師三大部與相關鈔疏的白話對照本，逐段原文與白話並列；原文採 CBETA 電子佛典（大正藏／卍續藏）。</p>' + '<p class="intro"><a href="appendix.html">附錄：名相與度量衡</a></p>'
                + ''.join(cards) + '<p class="byline"><a href="search.html">→ 全文搜尋</a></p>')
    io.open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page('目錄', idx_body))
    # 搜尋頁
    opts = ''.join('<option value="' + html.escape(b['id']) + '">' + html.escape(b['title']) + '</option>'
                   for b in search_books)
    sb = ('<h1>全文搜尋</h1>'
          '<p class="byline">站內全文：<code>Ctrl/⌘ K</code>；瀏覽器尋找仍用 <code>Ctrl/⌘ F</code>。'
          '可用 ↑↓ 選擇結果、Enter 開啟。</p>'
          '<div class="searchbar"><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" autocomplete="off" autofocus aria-label="全文搜尋">'
          '<select id="bookfilter" aria-label="限定書籍"><option value="">全部書籍</option>' + opts + '</select></div>'
          '<p class="byline" id="count"></p>'
          '<p id="searchstatus" class="sr-only" role="status" aria-live="polite"></p>'
          '<div id="searcherror" hidden></div>'
          '<div id="quickhits" hidden></div>'
          '<div id="hits"></div>')
    io.open(os.path.join(SITE, 'search.html'), 'w', encoding='utf-8').write(
        page('搜尋', sb, extra_scripts=['search/manifest.js', 'search.js']))
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
        for f in sorted(_g.glob(os.path.join(SITE, 'hebian', '*.html')),
                        key=lambda p: vol_order_key(os.path.basename(p)[:-5])):
            v = os.path.basename(f)[:-5]
            h2s = re.findall(r'<h2 class="sec" id="(p\d+)">([^<]+)</h2>', io.open(f, encoding='utf-8').read())
            hbv.append(dict(v=v, secs=[[a, b] for a, b in dict.fromkeys(h2s)]))
        if hbv:
            nav_books.append(dict(out='hebian', title='行事鈔資持記・句級合編', vols=hbv))
    except Exception as _e:
        print('hb nav', _e)
    io.open(os.path.join(SITE, 'nav.json'), 'w', encoding='utf-8').write(
        json.dumps(dict(books=nav_books), ensure_ascii=False))
    shutil.copyfile(os.path.join(B, '_src', 'nav.js'), os.path.join(SITE, 'nav.js'))
    print('nav.json', len(nav_books), 'books')

    # 附錄目前是唯一未由主生成器產生的靜態頁：只重包頁殼，正文原樣保留
    ap = os.path.join(SITE, 'appendix.html')
    if os.path.exists(ap):
        raw = io.open(ap, encoding='utf-8').read()
        m = re.search(r'<main\b[^>]*>(.*)</main>', raw, re.S)
        if m:
            body = re.sub(r'<footer\b.*?</footer>', '', m.group(1), flags=re.S)
            styles = ''.join(re.findall(r'<style\b[^>]*>.*?</style>', raw, re.S))
            styles = re.sub(r'#f4efe2', 'var(--surface-3)', styles, flags=re.I)
            io.open(ap, 'w', encoding='utf-8').write(
                SA.page('附錄：名相、音注與度量衡', body, prefix='', extra_head=styles))
            print('appendix shell rebuilt')


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

build()
