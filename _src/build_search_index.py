# -*- coding: utf-8 -*-
"""由「實際輸出頁面」重建全站搜尋索引（docs/search/*.js）。

為什麼要這樣做
--------------
首頁搜尋原本的索引由 site2.py 依 `TXT_分卷`＋`AI語譯/out` 產生，但六書頁面
後來是由 render_canonical_cb.py 依 `定稿/*.jsonl` 重建；兩邊來源不同，索引裡的
錨點（sN）在頁面上根本不存在，段落文字也和頁面所見不一致。

本模組改以 `docs/<book>/<vol>.html` 為唯一來源，索引條目和頁面 pair 一一對應。

錨點規則
--------
1. pair 本身已有 id（合編頁 sN）→ 直接沿用該 id。
2. pair 沒有 id → 用 `pair-<ordinal>`；ordinal 是 `main` 內第幾個 `.pair`
   （0 起算，含沒有原文的圖示 pair）。nav.js 會把 `pair-N` 解析成第 N 個
   `.pair`，捲到該段並高亮，所以不必手動改書頁 HTML。

用法
----
    python -X utf8 _src/build_search_index.py            # 重建全部
    python -X utf8 _src/build_search_index.py --only xingshichao
    python -X utf8 _src/build_search_index.py --check    # 只驗證，不寫檔
"""
import argparse
import html
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')

# 書名沿用站上目錄頁（docs/index.html）既有的顯示名稱；nav.json 只當後備。
BOOK_TITLES = {
    'xingshichao': '四分律刪繁補闕行事鈔',
    'jieshu': '四分律含注戒本疏行宗記',
    'yeshu': '四分律刪補隨機羯磨疏',
    'zhichi': '四分律行事鈔資持記',
    'nicao': '四分比丘尼鈔',
    'yichao': '四分律拾毗尼義鈔',
    'hebian': '四分律行事鈔資持記・句級合編',
}
BOOK_ORDER = ['xingshichao', 'jieshu', 'yeshu', 'zhichi', 'nicao', 'yichao', 'hebian']

PAIR_START = re.compile(r'<div class="pair(?:[^"]*)"([^>]*)>')
HEAD_RE = re.compile(r'<h2 class="sec"[^>]*>(.*?)</h2>', re.S)


def div_end(t, start):
    """回傳從 start 開始的 <div> 對應 </div> 之後的位置。"""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', t[start:]):
        depth += -1 if m.group(0) == '</div>' else 1
        if depth == 0:
            return start + m.end()
    return len(t)


def strip_text(inner):
    """把 pair 內的 HTML 轉成純文字：<br> 當換行，去標籤、還原實體。"""
    s = re.sub(r'<br\s*/?>', '\n', inner)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()


def first_div(block, cls):
    """取出 block 內第一個 class 以 cls 開頭的 div 內容（不含外層）。"""
    m = re.search(r'<div class="%s(?:[^"]*)"[^>]*>' % cls, block)
    if not m:
        return None
    end = div_end(block, m.start())
    return block[m.end():max(m.end(), end - len('</div>'))]


def pairs_of_page(t):
    """依頁面順序回傳所有 pair：[{ordinal, id, o, t, s}]（含沒有原文的圖示）。

    `s` 是該 pair 所屬的節標題（前面最近的 h2.sec）；搜尋結果用它顯示篇名。
    """
    heads = [(m.start(), strip_text(m.group(1)))
             for m in re.finditer(HEAD_RE, t)]
    out = []
    hi = -1
    for i, m in enumerate(PAIR_START.finditer(t)):
        while hi + 1 < len(heads) and heads[hi + 1][0] < m.start():
            hi += 1
        attrs = m.group(1) or ''
        start = m.start()
        end = div_end(t, start)
        block = t[start:end]
        pid = re.search(r'\bid="([^"]*)"', attrs)
        o = first_div(block, 'o')
        tr = first_div(block, 't')
        out.append(dict(ordinal=i,
                        id=(pid.group(1) if pid else ''),
                        o=strip_text(o) if o is not None else '',
                        t=strip_text(tr) if tr is not None else '',
                        s=(heads[hi][1] if hi >= 0 else '卷首')))
    return out


def _load_nav(site):
    p = os.path.join(site, 'nav.json')
    if not os.path.exists(p):
        return None
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return None


def book_volumes(site=SITE):
    """回傳 [(book, title, [vol...])]，卷序以 nav.json 為準。"""
    nav = _load_nav(site)
    books = []
    seen = set()
    if nav:
        for b in nav.get('books', []):
            out = b.get('out')
            if not out:
                continue
            vols = [v.get('v') for v in b.get('vols', []) if v.get('v')]
            books.append((out, BOOK_TITLES.get(out) or b.get('title') or out, vols))
            seen.add(out)
    d = os.path.join(site, 'hebian')
    for out in BOOK_ORDER:
        if out in seen:
            continue
        dirp = os.path.join(site, out)
        if not os.path.isdir(dirp):
            continue
        vols = sorted(f[:-5] for f in os.listdir(dirp) if f.endswith('.html'))
        books.append((out, BOOK_TITLES.get(out, out), vols))
        seen.add(out)
    # 補上 nav.json 有列、但目錄裡多出來的卷
    for i, (out, title, vols) in enumerate(books):
        dirp = os.path.join(site, out)
        if not os.path.isdir(dirp):
            continue
        have = set(vols)
        extra = sorted(f[:-5] for f in os.listdir(dirp)
                       if f.endswith('.html') and f[:-5] not in have)
        if extra:
            books[i] = (out, title, vols + extra)
    return books


def build_book(site, book, vols):
    entries = []
    n_pairs = n_id = n_ord = n_skip = 0
    for v in vols:
        p = os.path.join(site, book, v + '.html')
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding='utf-8').read()
        for pr in pairs_of_page(t):
            n_pairs += 1
            if not pr['o']:
                n_skip += 1
                continue
            if pr['id']:
                anchor = pr['id']
                n_id += 1
            else:
                anchor = 'pair-%d' % pr['ordinal']
                n_ord += 1
            entries.append(dict(v=v, o=pr['o'], t=pr['t'], i=anchor, n=pr['ordinal'] + 1,
                                s=pr.get('s') or ''))
    return dict(title=None, entries=entries), dict(
        book=book, pairs=n_pairs, entries=len(entries), id_anchor=n_id,
        ord_anchor=n_ord, skipped=n_skip)


def write_json_js(path, prefix, payload):
    tmp = path + '.tmp'
    io.open(tmp, 'w', encoding='utf-8', newline='\n').write(
        prefix + json.dumps(payload, ensure_ascii=False) + ';')
    os.replace(tmp, path)


def build(site=SITE, only=None, quiet=False):
    books = book_volumes(site)
    if only:
        want = set(only)
        books = [b for b in books if b[0] in want]
        missing = want - set(b[0] for b in books)
        if missing:
            raise SystemExit('找不到書：' + '、'.join(sorted(missing)))
    os.makedirs(os.path.join(site, 'search'), exist_ok=True)
    manifest = []
    stats = []
    for book, title, vols in books:
        data, st = build_book(site, book, vols)
        data['title'] = title
        write_json_js(os.path.join(site, 'search', book + '.js'),
                      'window.SIDX=window.SIDX||{};window.SIDX["%s"]=' % book, data)
        manifest.append(dict(id=book, title=title, file='search/' + book + '.js'))
        stats.append(st)
        if not quiet:
            print('%-12s 卷 %2d  pair %5d  索引 %5d（id %d／pair-N %d，跳過無原文 %d）'
                  % (book, len(vols), st['pairs'], st['entries'],
                     st['id_anchor'], st['ord_anchor'], st['skipped']))
    # manifest 只覆蓋本次建到的書；全量重建時即全部
    mp = os.path.join(site, 'search', 'manifest.js')
    if only:
        if not os.path.exists(mp):
            # 只重建單書（例如 site_hebian.py）且尚無 manifest：不要寫出殘缺清單
            return stats
        old = io.open(mp, encoding='utf-8').read()
        keep = [b for b in json.loads(re.search(r'=(\[.*\]);\s*$', old, re.S).group(1))
                if b['id'] not in set(x['id'] for x in manifest)]
        manifest = sorted(keep + manifest, key=lambda b: BOOK_ORDER.index(b['id'])
                          if b['id'] in BOOK_ORDER else 99)
    write_json_js(mp, 'window.SEARCH_BOOKS=', manifest)
    return stats


# ── 驗證 ────────────────────────────────────────────────────
def _norm(s):
    return re.sub(r'\s+', '', s or '')


def load_index(site, book):
    p = os.path.join(site, 'search', book + '.js')
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'=(\{.*\});\s*$', t, re.S)
    if not m:
        raise ValueError('索引格式錯誤：' + p)
    return json.loads(m.group(1))


def load_manifest(site=SITE):
    p = os.path.join(site, 'search', 'manifest.js')
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'=(\[.*\]);\s*$', t, re.S)
    return json.loads(m.group(1))


def verify(site=SITE, books=None):
    """檢查所有索引條目：頁面存在、錨點可解析、段落文字與頁面一致、n 正確。"""
    issues = []
    counts = dict(entries=0, anchor_id=0, anchor_ord=0, anchor_bad=0,
                  text_ok=0, text_bad=0, pages=0)
    cache = {}
    for b in load_manifest(site):
        if books and b['id'] not in books:
            continue
        data = load_index(site, b['id'])
        for e in data.get('entries', []):
            counts['entries'] += 1
            v = e.get('v', '')
            key = (b['id'], v)
            if key not in cache:
                p = os.path.join(site, b['id'], v + '.html')
                if not os.path.exists(p):
                    cache[key] = None
                else:
                    counts['pages'] += 1
                    cache[key] = pairs_of_page(io.open(p, encoding='utf-8').read())
            pairs = cache[key]
            if pairs is None:
                issues.append(('NOFILE', b['id'], v, e.get('i', '')))
                counts['anchor_bad'] += 1
                continue
            anchor = e.get('i') or ''
            pr = None
            if anchor.startswith('pair-') and anchor[5:].isdigit():
                n = int(anchor[5:])
                if 0 <= n < len(pairs):
                    pr = pairs[n]
                    counts['anchor_ord'] += 1
            if pr is None and anchor:
                for cand in pairs:
                    if cand['id'] == anchor:
                        pr = cand
                        counts['anchor_id'] += 1
                        break
            if pr is None:
                issues.append(('ANCHOR', b['id'], v, anchor))
                counts['anchor_bad'] += 1
                continue
            if e.get('n') is not None and e['n'] != pr['ordinal'] + 1:
                issues.append(('ORDER', b['id'], v, anchor, e['n'], pr['ordinal'] + 1))
            if _norm(e.get('o')) == _norm(pr['o']):
                counts['text_ok'] += 1
            else:
                counts['text_bad'] += 1
                issues.append(('TEXT', b['id'], v, anchor, (e.get('o') or '')[:30]))
    return counts, issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    if args.check:
        counts, issues = verify()
        for it in issues[:20]:
            print(it)
        print('search entries %(entries)d anchor(id %(anchor_id)d / pair-N %(anchor_ord)d) '
              'bad %(anchor_bad)d text_ok %(text_ok)d text_bad %(text_bad)d' % counts)
        sys.exit(1 if issues else 0)
    build(only=args.only, quiet=args.quiet)
    counts, issues = verify()
    print('verify: entries %(entries)d anchor_bad %(anchor_bad)d text_bad %(text_bad)d' % counts)
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
