# -*- coding: utf-8 -*-
"""把「一巻一頁」拆成「卷目錄頁 ＋ 一篇一頁」。

產出（不動渲染器；渲染器先跑，本程式最後跑）
------------------------------------------
1. `docs/<book>/<卷>.html` → **卷目錄頁**：只留
   `<h1>書名・卷</h1>`、byline（共 N 篇、M 段）、`<h2 class="sec" id="p-toc">本卷篇目</h2>`
   與篇連結清單（每篇附段數）；不含 pair。分頁列仍是**卷層級**（上一卷／下一卷）。
2. `docs/<book>/<卷>__p<N>.html` → **篇頁**：內容＝該篇原本的 `<h2 class="sec">…</h2>`
   到下一節前的完整 HTML（含 pair），外加原本的 `<h1>`（書名・卷）、篇 byline、
   footer 與 `</main>` 外的 `<nav class="pager">`。分頁列的 prev/next 是**全書篇序**
   （跨卷串接，label 用篇名），「目錄」連到該卷目錄頁。頂部列 `tb-volnav` 仍是卷層級。
3. `docs/nav.json`：維持 books → vols → secs 三層；卷條目 `v` 仍是卷目錄頁，
   `secs` 改為 `[[anchor_id, label, "<卷>__p<N>"], ...]`，讓側欄／首頁樹／搜尋捷徑
   都能直接指到篇頁。

設計要點
--------
* 卷頁若在第一個 `<h2 class="sec">` 前已有 pair（戒疏卷一、資治記兩卷、合編卷上之一
  的卷首內容），另立 `__p0`「卷首」篇頁，確保 pair 一段不漏。
* 篇頁 id 沿用原 h2 的 id（`p<N>`）；`__p<N>` 的 N 取該 id 的數字（合編的章號是
  全書章號，例如 `hebian/卷中之一__p13.html`）。卷首篇頁固定 `__p0`。
* 可重複執行：卷頁若已是目錄頁（有 `id="p-toc"`），改由既有 `*__p*.html` 重建，
  所有篇頁重寫、殘檔刪除；若卷頁仍是完整單頁，則重新切篇、覆寫目錄頁。
* 重新產生 `.new` 時不會動；本程式只寫入正式的 `.html`。

重建順序（必須照這個順序；渲染器會把卷頁蓋回單頁，切頁器一定要最後跑）
--------------------------------------------------------------------
    python -X utf8 _src/render_canonical_cb.py --apply     # 行事鈔/戒疏/業疏/尼鈔/義鈔
    python -X utf8 _src/render_zhichi.py                   # 資持記（先產 .new）
    python -X utf8 _src/render_zhichi.py --nav --apply     # 套用 .new
    python -X utf8 _src/render_static.py                   # 首頁/搜尋/附錄/未譯＋共用資源
    python -X utf8 _src/build_download_page.py
    python -X utf8 _src/site_hebian2.py                    # 合編
    python -X utf8 _src/split_by_section.py                # ← 本程式：切篇＋更新 nav.json
    python -X utf8 _src/build_search_index.py              # 全站搜尋索引（以篇頁為單位）
    python -X utf8 _src/validate_site.py

用法
----
    python -X utf8 _src/split_by_section.py                # 全部書
    python -X utf8 _src/split_by_section.py xingshichao    # 只處理指定書
"""
import argparse
import html
import io
import json
import os
import re
import sys

import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DOCS = os.path.join(B, 'docs')
NAV = os.path.join(DOCS, 'nav.json')

BOOKS = ['xingshichao', 'jieshu', 'yeshu', 'zhichi', 'nicao', 'yichao', 'hebian']

MAIN_OPEN = '<main id="main" tabindex="-1">'
MAIN_CLOSE = '</main>'
PAIR_OPEN = '<div class="pair'
TOC_MARK = 'id="p-toc"'

H1_RE = re.compile(r'<h1>(.*?)</h1>', re.S)
BYLINE_RE = re.compile(r'<p class="byline">(.*?)</p>', re.S)
SEC_RE = re.compile(r'<h2 class="sec"')
H2_RE = re.compile(r'<h2 class="sec"([^>]*)>(.*?)</h2>', re.S)
ID_RE = re.compile(r'\bid="([^"]+)"')
STEM_RE = re.compile(r'^(.+?)__p(\d+)\.html$')
VOL_TITLE_RE = re.compile(r'<title>.*?</title>', re.S)
DESC_RE = re.compile(r'<meta name="description" content="[^"]*">')
VER_RE = re.compile(r'\?v=\d+')
NAVVER_RE = re.compile(r'data-nav-version="\d+"')
# 渲染器 byline 可能以「共 N 段」結尾（卷頁）；卷目錄頁 byline 以「共 N 篇、M 段」結尾
VOL_COUNT_SUFFIX = re.compile(r'｜共\s*\d+\s*段\s*$')
TOC_COUNT_SUFFIX = re.compile(r'｜共\s*\d+\s*篇、\d+\s*段\s*$')


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s or '')


def refresh_assets(s):
    """把頁殼內的資源版本統一成目前的 ASSET_VERSION（切頁器輸出永遠最新）。"""
    s = VER_RE.sub('?v=' + SA.ASSET_VERSION, s)
    return NAVVER_RE.sub('data-nav-version="' + SA.ASSET_VERSION + '"', s)


def page_parts(t):
    """回傳 (prefix, main_html, post_html)。

    prefix 到 `<main …>` 開標籤為止；post 由 `</main>` 起（含 pager、footer、收尾）。
    """
    i0 = t.find(MAIN_OPEN)
    if i0 < 0:
        raise SystemExit('找不到 <main> 開標籤：' + MAIN_OPEN)
    i0 += len(MAIN_OPEN)
    i1 = t.find(MAIN_CLOSE, i0)
    if i1 < 0:
        raise SystemExit('找不到 </main>')
    return t[:i0], t[i0:i1], t[i1:]


def is_toc_page(main_html):
    return TOC_MARK in main_html


def parse_head(main_html, where=''):
    """解析 `<h1>` 與緊接的 `<p class="byline">`。

    回傳 (h1_html, h1_text, byline_raw, head_end)；head_end 是 byline 結束後的位移。
    """
    m1 = H1_RE.search(main_html)
    if not m1:
        raise SystemExit('缺少 <h1>：' + where)
    between = main_html[m1.end():].lstrip()
    if not between.startswith('<p class="byline">'):
        raise SystemExit('<h1> 後沒有緊接 byline：' + where)
    mb = BYLINE_RE.search(main_html, m1.end())
    if not mb:
        raise SystemExit('byline 沒有結束標籤：' + where)
    h1_text = html.unescape(strip_tags(m1.group(1))).strip()
    if not h1_text:
        raise SystemExit('<h1> 是空的：' + where)
    byline = mb.group(1).strip()
    return main_html[m1.start():m1.end()], h1_text, byline, mb.end()


def split_sections(main_html, head_end, where=''):
    """回傳 (pre_rest, sections)。sections = [{id,label,chunk,pairs}]。"""
    pos = [m.start() for m in SEC_RE.finditer(main_html, head_end)]
    pre_rest = main_html[head_end:pos[0]] if pos else main_html[head_end:]
    sections = []
    used = set()
    for i, p in enumerate(pos):
        end = pos[i + 1] if i + 1 < len(pos) else len(main_html)
        chunk = main_html[p:end]
        m = H2_RE.match(chunk)
        if not m:
            raise SystemExit('h2.sec 解析失敗：' + where)
        attrs, label_raw = m.group(1), m.group(2)
        mid = ID_RE.search(attrs)
        if not mid:
            raise SystemExit('h2.sec 沒有 id：' + where)
        sid = mid.group(1)
        if sid in used:
            raise SystemExit('同一卷 h2 id 重複 %r：%s' % (sid, where))
        used.add(sid)
        label = html.unescape(strip_tags(label_raw)).strip()
        if not label:
            raise SystemExit('h2.sec 標題是空的：' + where)
        sections.append(dict(id=sid, label=label, chunk=chunk,
                             pairs=chunk.count(PAIR_OPEN)))
    return pre_rest, sections


def stem_of(vol, sid, ordinal):
    """篇頁 stem：`<卷>__p<N>`；N 取 h2 id 的數字，非 pN 格式才退回篇序。"""
    m = re.match(r'^p(\d+)$', sid or '')
    n = int(m.group(1)) if m else ordinal
    return '%s__p%d' % (vol, n)


def volume_articles_full(vol, t):
    """完整單頁 → 卷目錄資料 ＋ 篇頁資料（不寫檔）。"""
    prefix, main, post = page_parts(t)
    h1_html, h1_text, vol_byline, head_end = parse_head(main, vol)
    pre_rest, sections = split_sections(main, head_end, vol)
    vol_pairs = main.count(PAIR_OPEN)
    base_byline = VOL_COUNT_SUFFIX.sub('', vol_byline).strip()
    if not base_byline:
        raise SystemExit('byline 解析為空：' + vol)
    articles = []
    if PAIR_OPEN in pre_rest:
        # 卷首內容（h2 前已有 pair）：另立 `__p0` 篇頁，標題「卷首」
        articles.append(dict(id='p0', label='卷首', kind='shou',
                             chunk='<h2 class="sec" id="p0">卷首</h2>' + pre_rest,
                             pairs=pre_rest.count(PAIR_OPEN)))
    for i, sec in enumerate(sections):
        art = dict(id=sec['id'], label=sec['label'], kind='sec',
                   chunk=sec['chunk'], pairs=sec['pairs'], ordinal=i + 1)
        if not articles and pre_rest.strip():
            # h2 前的非 pair 殘留（正常為空）：併進第一篇，避免內容遺失
            art['chunk'] = pre_rest + art['chunk']
        articles.append(art)
    if not articles:
        raise SystemExit('%s 沒有任何 <h2 class="sec">，無法切篇' % vol)
    for i, art in enumerate(articles):
        art['stem'] = stem_of(vol, art['id'], i + 1)
    stems = [a['stem'] for a in articles]
    if len(set(stems)) != len(stems):
        raise SystemExit('%s 篇頁 stem 重複：%s' % (vol, stems))
    got = sum(a['pairs'] for a in articles)
    if got != vol_pairs:
        raise SystemExit('%s pair 數不符：切篇 %d ≠ 原頁 %d' % (vol, got, vol_pairs))
    if any(a['pairs'] <= 0 for a in articles):
        raise SystemExit('%s 有 0 段的篇：%s'
                         % (vol, [(a['stem'], a['pairs']) for a in articles]))
    nsec = len([a for a in articles if a['kind'] == 'sec'])
    for i, art in enumerate(articles):
        art['pos_label'] = ('卷首' if art['kind'] == 'shou'
                            else '本卷 第 %d／%d 篇' % (art['ordinal'], nsec))
        art['byline'] = (base_byline + '｜' + art['pos_label']
                         + '｜共 %d 段' % art['pairs'])
        art['title'] = h1_text + '\u3000' + art['label']
        art['desc'] = art['title'] + '：原文與白話逐段對照。'
    return dict(vol=vol, mode='full', prefix=prefix, post=post,
                h1_html=h1_html, h1_text=h1_text, base_byline=base_byline,
                pairs=vol_pairs, articles=articles, nsec=nsec)


def volume_articles_toc(book, vol, t):
    """已是卷目錄頁 → 由既有 `*__p*.html` 重建（可重跑）。"""
    prefix, main, post = page_parts(t)
    h1_html, h1_text, toc_byline, _head_end = parse_head(main, vol)
    base_byline = TOC_COUNT_SUFFIX.sub('', toc_byline).strip()
    if not base_byline:
        raise SystemExit('卷目錄頁 byline 解析為空：' + vol)
    art_dir = os.path.join(DOCS, book)
    files = []
    for f in os.listdir(art_dir):
        m = STEM_RE.match(f)
        if m and m.group(1) == vol:
            files.append((int(m.group(2)), f))
    if not files:
        raise SystemExit('%s 是卷目錄頁但找不到任何 %s__p*.html；'
                         '請先重跑渲染器再切篇' % (vol, vol))
    files.sort()
    articles = []
    for _n, f in files:
        stem = f[:-5]
        at = read(os.path.join(art_dir, f))
        _ap, amain, _apost = page_parts(at)
        _ah1, _ah1t, _ab, ahead_end = parse_head(amain, stem)
        chunk = amain[ahead_end:]
        m = H2_RE.match(chunk)
        if not m:
            raise SystemExit('%s 缺少 <h2 class="sec">' % stem)
        mid = ID_RE.search(m.group(1))
        if not mid:
            raise SystemExit('%s 的 h2.sec 沒有 id' % stem)
        sid = mid.group(1)
        label = html.unescape(strip_tags(m.group(2))).strip()
        pairs = chunk.count(PAIR_OPEN)
        # 既有篇頁只當內容來源；byline 重新由卷目錄頁的 base 產生
        articles.append(dict(id=sid, label=label,
                             kind=('shou' if sid == 'p0' else 'sec'),
                             chunk=chunk, pairs=pairs))
    articles.sort(key=lambda a: (0 if a['id'] == 'p0' else 1,
                                 int(a['id'][1:]) if re.match(r'^p\d+$', a['id'])
                                 else 10 ** 9))
    nsec = len([a for a in articles if a['kind'] == 'sec'])
    sec_i = 0
    for i, art in enumerate(articles):
        if art['kind'] == 'shou':
            art['pos_label'] = '卷首'
            if art['id'] != 'p0':
                raise SystemExit('%s 卷首篇 id 應為 p0' % vol)
        else:
            sec_i += 1
            art['pos_label'] = '本卷 第 %d／%d 篇' % (sec_i, nsec)
        art['stem'] = stem_of(vol, art['id'], i + 1)
        art['byline'] = (base_byline + '｜' + art['pos_label']
                         + '｜共 %d 段' % art['pairs'])
        art['title'] = h1_text + '\u3000' + art['label']
        art['desc'] = art['title'] + '：原文與白話逐段對照。'
    vol_pairs = sum(a['pairs'] for a in articles)
    if any(a['pairs'] <= 0 for a in articles):
        raise SystemExit('%s 有 0 段的篇：%s'
                         % (vol, [(a['stem'], a['pairs']) for a in articles]))
    return dict(vol=vol, mode='toc', prefix=prefix, post=post,
                h1_html=h1_html, h1_text=h1_text, base_byline=base_byline,
                pairs=vol_pairs, articles=articles, nsec=nsec)


def replace_pager(post, pager_html):
    """把 post（`</main>` 之後）裡唯一的分頁列換掉；沒有就報錯。"""
    i = post.find('<nav class="pager"')
    if i < 0:
        raise SystemExit('post 區找不到 <nav class="pager">')
    j = post.find('</nav>', i)
    if j < 0:
        raise SystemExit('<nav class="pager"> 沒有 </nav>')
    return post[:i] + pager_html + post[j + len('</nav>'):]


def article_head(prefix, title, desc):
    def _title(_m):
        return ('<title>' + html.escape(title) + '｜南山律典・白話對照</title>')

    def _desc(_m):
        return ('<meta name="description" content="' + html.escape(desc) + '">')

    s = VOL_TITLE_RE.sub(_title, prefix, count=1)
    s = DESC_RE.sub(_desc, s, count=1)
    return refresh_assets(s)


def build_toc_main(info):
    arts = info['articles']
    parts = [info['h1_html'],
             '<p class="byline">%s｜共 %d 篇、%d 段</p>'
             % (info['base_byline'], len(arts), info['pairs']),
             '<h2 class="sec" id="p-toc">本卷篇目</h2>',
             '<ul class="voltoc">']
    for art in arts:
        parts.append('<li><a href="%s.html"><span class="tn">%s</span>'
                     '<span class="n">%d 段</span></a></li>'
                     % (art['stem'], html.escape(art['label']), art['pairs']))
    parts.append('</ul>')
    return ''.join(parts)


def natural_key(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]


def process_book(book, nav_book):
    d = os.path.join(DOCS, book)
    if not os.path.isdir(d):
        print('SKIP %-12s（docs/%s 不存在）' % (book, book))
        return 0, 0
    # 卷序：nav.json 既有順序優先；目錄裡多出來的完整卷頁再依自然序補在後面
    vols = []
    for v in nav_book.get('vols') or []:
        name = v.get('v')
        if not name:
            continue
        if not os.path.exists(os.path.join(d, name + '.html')):
            raise SystemExit('%s 的卷頁不存在：%s.html（請先跑渲染器）'
                             % (book, name))
        if name not in vols:
            vols.append(name)
    extra = []
    for f in os.listdir(d):
        if not f.endswith('.html') or STEM_RE.match(f):
            continue
        stem = f[:-5]
        if stem not in vols:
            extra.append(stem)
    if extra:
        print('WARN %-12s nav.json 沒有的卷頁：%s（一併處理）'
              % (book, '、'.join(sorted(extra, key=natural_key))))
        vols += sorted(extra, key=natural_key)
    if not vols:
        raise SystemExit('%s 找不到任何卷頁' % book)

    infos = []
    for vol in vols:
        t = read(os.path.join(d, vol + '.html'))
        _prefix, main, _post = page_parts(t)
        if is_toc_page(main):
            info = volume_articles_toc(book, vol, t)
        else:
            info = volume_articles_full(vol, t)
        infos.append(info)

    # 全書篇序（跨卷）→ 每篇頁的 prev/next
    seq = [(vi, art) for vi, info in enumerate(infos) for art in info['articles']]
    stems = [art['stem'] for _vi, art in seq]
    if len(set(stems)) != len(stems):
        dup = sorted({s for s in stems if stems.count(s) > 1})
        raise SystemExit('%s 篇頁 stem 跨卷重複：%s' % (book, dup))
    total_pairs = 0
    for si, (vi, art) in enumerate(seq):
        prev_art = seq[si - 1][1] if si > 0 else None
        next_art = seq[si + 1][1] if si + 1 < len(seq) else None
        art['prev_url'] = prev_art['stem'] + '.html' if prev_art else None
        art['prev_label'] = prev_art['label'] if prev_art else None
        art['next_url'] = next_art['stem'] + '.html' if next_art else None
        art['next_label'] = next_art['label'] if next_art else None

    # 寫篇頁
    for vi, info in enumerate(infos):
        for art in info['articles']:
            pager = SA.pager_html(art['prev_url'], art['next_url'],
                                  art['prev_label'], art['next_label'],
                                  info['vol'] + '.html', aria_label='篇導覽')
            out = (article_head(info['prefix'], art['title'], art['desc'])
                   + info['h1_html']
                   + '<p class="byline">' + art['byline'] + '</p>'
                   + art['chunk']
                   + replace_pager(refresh_assets(info['post']), pager))
            write(os.path.join(d, art['stem'] + '.html'), out)
            total_pairs += art['pairs']

    # 清掉不在本次篇序裡的殘檔（例如舊版切頁、改號後的舊篇頁）
    expected = {art['stem'] + '.html' for _vi, art in seq}
    stale = sorted(f for f in os.listdir(d)
                   if STEM_RE.match(f) and f not in expected)
    for f in stale:
        os.remove(os.path.join(d, f))
    if stale:
        print('  %-12s 清殘檔 %d：%s' % (book, len(stale), '、'.join(stale[:6])))

    # 寫卷目錄頁（篇頁寫完才覆蓋，崩潰時卷頁仍是完整頁可重切）
    for info in infos:
        toc = (refresh_assets(info['prefix'])
               + build_toc_main(info)
               + refresh_assets(info['post']))
        write(os.path.join(d, info['vol'] + '.html'), toc)

    nav_book['vols'] = [
        {'v': info['vol'],
         'secs': [[art['id'], art['label'], art['stem']] for art in info['articles']]}
        for info in infos]
    n_articles = sum(len(info['articles']) for info in infos)
    print('%-12s %2d 卷 → %3d 篇頁（%6d 段）' % (book, len(infos), n_articles, total_pairs))
    return n_articles, total_pairs


def main():
    ap = argparse.ArgumentParser(description='一巻一頁 → 卷目錄＋一篇一頁')
    ap.add_argument('books', nargs='*', choices=BOOKS,
                    help='只處理指定書（預設全部）')
    args = ap.parse_args()
    books = args.books or BOOKS

    nav = json.load(io.open(NAV, encoding='utf-8'))
    by_out = {b.get('out'): b for b in nav.get('books', [])}
    total_articles = total_pairs = 0
    for book in books:
        nb = by_out.get(book)
        if not nb:
            raise SystemExit('nav.json 找不到書：' + book)
        a, p = process_book(book, nb)
        total_articles += a
        total_pairs += p

    tmp = NAV + '.tmp'
    write(tmp, json.dumps(nav, ensure_ascii=False, indent=1) + '\n')
    os.replace(tmp, NAV)
    print('TOTAL 篇頁 %d、段 %d；nav.json 已更新' % (total_articles, total_pairs))
    return 0


if __name__ == '__main__':
    sys.exit(main())
