# -*- coding: utf-8 -*-
"""搜尋結果抽查：模擬 search.js 的比對／排序，驗證每筆結果的錨點與段落。

用法：
    python -X utf8 _src/check_search_links.py
    python -X utf8 _src/check_search_links.py --keywords 波羅夷 中國 --per-book 2
    python -X utf8 _src/check_search_links.py --out _tmp/search_spotcheck.md
"""
import argparse
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_search_index as BSI  # noqa: E402

DEFAULT_KEYWORDS = ['波羅夷', '中國', '受戒', '十三步', '羯磨',
                    '安居', '波羅提木叉', '僧殘', '說戒', '自恣']


def norm(s):
    return (s or '').lower()


def score(e, terms, phrase):
    o, t, v = norm(e.get('o')), norm(e.get('t')), norm(e.get('v'))
    s = 0
    if o.startswith(phrase):
        s += 12
    if phrase in o:
        s += 7
    if phrase in t:
        s += 3
    if phrase in v:
        s += 5
    for term in terms:
        if o.startswith(term):
            s += 4
        elif term in o:
            s += 2
        if term in t:
            s += 1
        if term in v:
            s += 1
    return s


def matches(e, terms):
    hay = norm(e.get('o')) + '\n' + norm(e.get('t')) + '\n' + norm(e.get('v'))
    return all(t in hay for t in terms)


def snippet(text, term, width=46):
    i = norm(text).find(norm(term))
    if i < 0:
        i = 0
    a = max(0, i - width // 2)
    b = min(len(text), a + width)
    return ('…' if a else '') + text[a:b].replace('\n', ' ') + ('…' if b < len(text) else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keywords', nargs='*', default=DEFAULT_KEYWORDS)
    ap.add_argument('--per-book', type=int, default=1, help='每個關鍵詞每本書取幾筆（預設 1）')
    ap.add_argument('--out', help='另存 markdown 表格')
    args = ap.parse_args()

    manifest = BSI.load_manifest()
    data = {b['id']: BSI.load_index(BSI.SITE, b['id']) for b in manifest}
    titles = {b['id']: b['title'] for b in manifest}

    rows = []
    bad = 0
    for kw in args.keywords:
        terms = [x for x in kw.split() if x]
        phrase = norm(kw)
        hits = []
        order = 0
        for b in manifest:
            for e in data[b['id']].get('entries', []):
                if matches(e, terms):
                    hits.append((b['id'], e, score(e, terms, phrase), order))
                order += 1
        hits.sort(key=lambda x: (-x[2], x[3]))
        if not hits:
            rows.append((kw, '—', '—', '—', 'NO_HIT', ''))
            bad += 1
            continue
        seen = {}
        picked = []
        for bid, e, sc, _o in hits:
            seen[bid] = seen.get(bid, 0) + 1
            if seen[bid] <= args.per_book:
                picked.append((bid, e, sc))
        for bid, e, sc in picked:
            page = os.path.join(BSI.SITE, bid, e['v'] + '.html')
            status = 'OK'
            if not os.path.exists(page):
                status = 'PAGE_MISSING'
            else:
                pairs = BSI.pairs_of_page(io.open(page, encoding='utf-8').read())
                pr = None
                a = e.get('i') or ''
                if a.startswith('pair-') and a[5:].isdigit():
                    n = int(a[5:])
                    pr = pairs[n] if 0 <= n < len(pairs) else None
                if pr is None:
                    pr = next((p for p in pairs if p['id'] == a), None)
                if pr is None:
                    status = 'ANCHOR_BAD'
                elif pr['ordinal'] + 1 != e.get('n'):
                    status = 'N_BAD'
                elif norm(e.get('o')) != norm(pr['o']):
                    status = 'TEXT_BAD'
                elif not any(t in (norm(pr['o']) + norm(pr['t'])) for t in terms):
                    status = 'KW_MISSING'
            if status != 'OK':
                bad += 1
            rows.append((kw, titles[bid], e['v'], a, str(e.get('n', '')), status, snippet(e.get('o', ''), terms[0])))

    print('| 關鍵詞 | 書 | 卷 | anchor | 段 | 驗證 | 命中原文（節錄） |')
    print('|:--|:--|:--|:--|--:|:--:|:--|')
    for r in rows:
        print('| %s | %s | %s | `%s` | %s | %s | %s |' % r)
    print('\n關鍵詞 %d 個，結果 %d 筆，驗證失敗 %d 筆'
          % (len(args.keywords), len(rows), bad))

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            f.write('| 關鍵詞 | 書 | 卷 | anchor | 段 | 驗證 | 命中原文（節錄） |\n')
            f.write('|:--|:--|:--|:--|--:|:--:|:--|\n')
            for r in rows:
                f.write('| %s | %s | %s | `%s` | %s | %s | %s |\n' % r)
            f.write('\n關鍵詞 %d 個，結果 %d 筆，驗證失敗 %d 筆\n'
                    % (len(args.keywords), len(rows), bad))
        print('已寫入', args.out)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
