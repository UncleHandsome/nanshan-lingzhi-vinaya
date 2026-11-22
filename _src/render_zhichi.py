# -*- coding: utf-8 -*-
"""資持記網站頁面生成器：定稿/zhichi.jsonl -> docs/zhichi/*.html.new。

用法
----
python -X utf8 _src/render_zhichi.py            只產生 .new
python -X utf8 _src/render_zhichi.py --nav      產生 .new，並更新 docs/nav.json
python -X utf8 _src/render_zhichi.py --apply    把已產生的 .new 原子替換成 .html

規則
----
* 依 16 卷分頁（上一上 … 下四），卷內依 30 篇標題分節。
* 節錨點由標題產生：每見一個篇題，依序給 p1、p2…，標籤用篇題，不手寫 id。
* 段別標籤完全依定稿 `label`（本書為【記文】）。
* 原文段落換行只輸出單一 `<br>`，絕不輸出 `<br><br>`。
* 卷末校勘 25 筆（key 4158–4182）依 AGENTS 0.5 不譯，不進 pair，只如實統計。
* 科判樹狀圖（含 ┌┐└┘│─ 等）以 `<pre>` 保留空格與行位，不當成散文長段。
* 不動五書內容；只替換 docs/zhichi 的 `<main>`。
"""
import argparse
import collections
import html
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DATA = os.path.join(B, '定稿', 'zhichi.jsonl')
DOCS = os.path.join(B, 'docs', 'zhichi')
NAV = os.path.join(B, 'docs', 'nav.json')

PAGES = ['上一上', '上一下', '上二', '上三', '上四',
         '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
         '下一', '下二', '下三', '下四']

TITLES = ['釋標宗篇', '釋集僧篇', '釋足數篇', '釋受欲篇', '釋羯磨篇',
          '釋結界篇', '釋僧網篇', '釋受戒篇', '釋師資篇', '釋說戒篇',
          '釋安居篇', '釋自恣篇', '釋篇聚篇', '釋釋相篇', '釋持犯篇',
          '釋懺六聚法篇', '釋二衣篇', '釋四藥篇', '釋鉢器篇', '釋對施篇',
          '釋頭陀篇', '釋僧像篇', '釋訃請篇', '釋導俗篇', '釋主客篇',
          '釋瞻病篇', '釋諸雜篇', '釋沙彌篇', '釋尼眾篇', '釋諸部篇']

BOOK_TITLE = '四分律行事鈔資持記'
BYLINE = '宋·元照律師　·　行事鈔之註　｜　白話對照'
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')
PUNCT = re.compile(r'[，。；：！？、]')
HEAD_RE = re.compile(r'(\d{1,2})\s*(釋[\u4e00-\u9fff]{1,10}篇)\s*[（(]([^）)]{1,16})[）)]')
BOX = re.compile(r'[┌┐└┘│─├┤┬┴┼]')


def rd(p):
    return io.open(p, encoding='utf-8').read()


def fmt(text):
    """原文／白話共用：段落換行一律單一 <br>，不留 <br><br>。"""
    s = html.escape(text or '')
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = re.sub(r'[ \t]*\n[\s]*', '<br>', s)
    s = re.sub(r'(?:<br>)+', '<br>', s)
    s = s.strip()
    s = re.sub(r'^(?:<br>)+|(?:<br>)+$', '', s)
    assert '<br><br>' not in s
    return s


def fmt_pre(text):
    """科判圖：完整保留空格與換行，只做 HTML escape。"""
    s = html.escape(text or '')
    assert '<br><br>' not in s
    return s


def page_of(row):
    chunk = row.get('chunk') or ''
    return chunk.split('_', 1)[1] if '_' in chunk else chunk


def pair_text(row):
    segs = row.get('segments') or []
    seg = segs[0] if segs else row
    label = seg.get('label') or row.get('label') or '記文'
    if label not in LABELS:
        label = '記文'
    src = seg.get('source') or row.get('source') or ''
    disp = seg.get('display_source') or row.get('display_source') or ''
    shown = disp if disp and PUNCT.search(disp) else src
    tr = seg.get('translation') or row.get('translation') or ''
    # row 的 translation 帶【記文】前綴；segment 的沒有。統一取 segment -> 去前綴。
    tr = re.sub(r'^\s*(?:【(?:疏文|記文|鈔文|律文|註文|序文)】\s*)+', '', tr.strip())
    return label, src, shown, tr


def load_rows():
    rows = [json.loads(x) for x in io.open(DATA, encoding='utf-8') if x.strip()]
    if not rows:
        sys.exit('ERROR: 定稿/zhichi.jsonl 為空')
    if len(rows) != 4182:
        sys.exit('ERROR: 定稿筆數 %d，預期 4182' % len(rows))
    missing = [r.get('key') for r in rows if r.get('raw_start', -1) < 0]
    if missing:
        sys.exit('ERROR: 未定位 %d 筆：%s' % (len(missing), missing[:10]))
    # 依 raw 起點排，同起點再依 key 數值
    rows.sort(key=lambda r: (r.get('raw_start', 10 ** 9), int(r.get('key', 0))))
    seen = []
    for r in rows:
        p = page_of(r)
        if p not in PAGES:
            sys.exit('ERROR: 未知分頁 %r（key %s）' % (p, r.get('key')))
        if not seen or seen[-1] != p:
            seen.append(p)
    if seen != PAGES:
        sys.exit('ERROR: 分頁順序不符：%s' % seen)
    return rows


def extract_heading(shown, page, found):
    """回傳 (num, title, marker) 或 None；標題由經文篇題取得。"""
    m = HEAD_RE.search(shown)
    if not m:
        return None
    num, title, marker = int(m.group(1)), m.group(2), m.group(3)
    if not (1 <= num <= 30):
        sys.exit('ERROR: 篇號 %d 越界（%s）' % (num, page))
    if TITLES[num - 1] != title:
        sys.exit('ERROR: 第 %d 篇標題 %r，預期 %r' % (num, title, TITLES[num - 1]))
    head_page = marker.split('-', 1)[0]
    if head_page != page:
        sys.exit('ERROR: 第 %d 篇標記 %r 與分頁 %r 不符' % (num, marker, page))
    found.append((page, num, title, marker))
    # 原文保留完整（含篇題與卷頁標記），h2 只負責導覽錨點；不刪原文任何字。
    return num, title, marker


def render_page(page, rows):
    out = ['<h1>%s　%s</h1>' % (BOOK_TITLE, page),
           '<p class="byline">%s</p>' % BYLINE]
    found = []
    pairs = 0
    diagrams = 0
    skipped = []
    for r in rows:
        label, src, shown, tr = pair_text(r)
        if not tr.strip():
            skipped.append(r.get('key'))
            continue
        head = extract_heading(shown, page, found)
        if head:
            num, title, marker = head
            sid = 'p%d' % len(found)
            out.append('<h2 class="sec" id="%s">%s</h2>'
                       % (sid, html.escape(title)))
        body_esc = fmt(shown)
        tr_esc = fmt(tr)
        if BOX.search(src):
            diagrams += 1
            out.append(
                '<div class="pair j ko"><pre class="ko" style="white-space:pre;overflow-x:auto;'
                'margin:0 0 .45rem;padding:.45rem .8rem;background:var(--ji-bg,#eef5f8);'
                'border-left:3px solid var(--ji-border,#3f6f8f);color:var(--ji-fg,#1f4e6b);'
                'font-size:13px;line-height:1.45;border-radius:0 4px 4px 0">'
                '【%s】%s</pre><div class="t">【%s】%s</div></div>'
                % (label, fmt_pre(shown), label, tr_esc))
        else:
            out.append('<div class="pair j"><div class="o ji">【%s】%s</div>'
                       '<div class="t">【%s】%s</div></div>'
                       % (label, body_esc, label, tr_esc))
        pairs += 1
    return out, found, pairs, diagrams, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nav', action='store_true', help='由 .new 更新 docs/nav.json 的 zhichi 章節')
    ap.add_argument('--apply', action='store_true', help='把既有 .new 原子替換成 .html')
    args = ap.parse_args()

    rows = load_rows()
    by_page = collections.OrderedDict((p, []) for p in PAGES)
    for r in rows:
        by_page[page_of(r)].append(r)

    if args.apply:
        for p in PAGES:
            new = os.path.join(DOCS, p + '.html.new')
            if not os.path.exists(new):
                sys.exit('ERROR: 缺少 %s，先跑不帶 --apply 的生成' % new)
        for p in PAGES:
            src = os.path.join(DOCS, p + '.html.new')
            dst = os.path.join(DOCS, p + '.html')
            os.replace(src, dst)
            print('applied %s' % dst)
        return

    total_pairs = 0
    total_diagrams = 0
    all_skipped = []
    all_headings = []
    page_pairs = {}
    page_secs = {}
    for p in PAGES:
        body, found, pairs, diagrams, skipped = render_page(p, by_page[p])
        all_headings.extend(found)
        total_pairs += pairs
        total_diagrams += diagrams
        all_skipped.extend(skipped)
        page_pairs[p] = pairs
        page_secs[p] = [('p%d' % (i + 1), t)
                        for i, (_pg, _n, t, _m) in enumerate(found)]

        old_path = os.path.join(DOCS, p + '.html')
        old = rd(old_path)
        m = re.search(r'<main id="main">(.*?)</main>', old, re.S)
        if not m:
            sys.exit('ERROR: %s 找不到 <main id="main">' % old_path)
        old_main = m.group(1)
        pager = re.search(r'<div class="pager">.*?</div>', old_main, re.S)
        footer = re.search(r'<footer class="sitefoot">.*?</footer>', old_main, re.S)
        tail = (pager.group(0) if pager else '') + (footer.group(0) if footer else '')
        new_main = '<main id="main">' + ''.join(body) + tail + '</main>'
        new = old[:m.start()] + new_main + old[m.end():]
        assert '<br><br>' not in new, p
        io.open(old_path + '.new', 'w', encoding='utf-8', newline='\n').write(new)
        print('%s pairs=%d diagrams=%d -> %s.new' % (p, pairs, diagrams, old_path))

    # 標題總檢查：30 篇、篇號 1..30、每篇一次
    nums = [n for (_p, n, _t, _m) in all_headings]
    if nums != list(range(1, 31)):
        sys.exit('ERROR: 篇標題序列不符：%s' % nums)

    if total_pairs != 4157:
        sys.exit('ERROR: pair 數 %d，預期 4157（4182 筆 - 25 筆卷末校勘）' % total_pairs)
    if len(all_skipped) != 25:
        sys.exit('ERROR: 未譯筆數 %d，預期 25' % len(all_skipped))

    print('TOTAL pages=%d pairs=%d diagrams=%d headings=%d skipped=%d'
          % (len(PAGES), total_pairs, total_diagrams, len(all_headings), len(all_skipped)))
    print('PAGE_PAIRS ' + json.dumps(page_pairs, ensure_ascii=False))
    print('SKIPPED_KEYS ' + ','.join(all_skipped))

    if args.nav:
        nav = json.load(io.open(NAV, encoding='utf-8'))
        hit = 0
        for b in nav.get('books', []):
            if b.get('out') == 'zhichi':
                b['vols'] = [{'v': p, 'secs': [[sid, label] for sid, label in page_secs[p]]}
                             for p in PAGES]
                hit += 1
        if hit != 1:
            sys.exit('ERROR: nav.json 找不到唯一的 zhichi 條目（找到 %d）' % hit)
        io.open(NAV, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(nav, ensure_ascii=False, indent=1) + '\n')
        print('NAV updated: %s (secs %s)' % (NAV, {p: len(page_secs[p]) for p in PAGES}))


if __name__ == '__main__':
    main()
