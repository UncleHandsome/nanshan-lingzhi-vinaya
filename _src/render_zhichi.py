# -*- coding: utf-8 -*-
"""資持記網站頁面生成器：定稿/zhichi.jsonl -> docs/zhichi/*.html.new。

用法
----
python -X utf8 _src/render_zhichi.py            只產生 .new
python -X utf8 _src/render_zhichi.py --nav      產生 .new，並更新 docs/nav.json
python -X utf8 _src/render_zhichi.py --apply    把已產生的 .new 原子替換成 .html

規則（2026-11-23 網站改善）
--------------------------
* 依 16 卷分頁（上一上 … 下四），卷內依 30 篇標題分節。
* 沒有篇題的 5 卷補節：上一上 →「卷首」；中一下／中二／中三上／中三下 →
  「第14篇　隨戒釋相（續一～續四）」。每卷至少 1 節。
* 節標題一律 `第N篇　短名`（canon_titles 共用），續篇加續標記；原典篇題仍在正文。
* 段別標籤只標原文欄；本書全為記文 → byline 說明「本卷：記文」。
* 每個 pair 加由定稿 key 衍生的穩定 id（`u…`）。
* 原文／白話／卷末導覽／頁尾都由 site_assets 產生，頁尾在 `</main>` 之外。
* 卷末校勘 25 筆（key 4158–4182）依 AGENTS 0.5 不譯，不進 pair，只如實統計。
* 科判樹狀圖以 `<pre>` 保留空格與行位。
"""
import argparse
import collections
import html
import io
import json
import os
import re
import sys

import canon_titles as CT
import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DATA = os.path.join(B, '定稿', 'zhichi.jsonl')
DOCS = os.path.join(B, 'docs', 'zhichi')
NAV = os.path.join(B, 'docs', 'nav.json')

PAGES = ['上一上', '上一下', '上二', '上三', '上四',
         '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
         '下一', '下二', '下三', '下四']

# 原典 30 篇題（只作核對；顯示用 canon_titles.TITLES）
TITLES = [CT.ZHICHI_TITLES[i] for i in range(1, 31)]

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


def find_heading(shown, page):
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
        sys.exit('ERROR: 第 %d 篇標記 %r 與分頁 %r 不符（%s）' % (num, marker, page, head_page))
    return num, title, marker


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nav', action='store_true', help='由 .new 更新 docs/nav.json 的 zhichi 章節')
    ap.add_argument('--apply', action='store_true', help='把既有 .new 原子替換成 .html')
    args = ap.parse_args()

    if args.apply:
        for p in PAGES:
            new = os.path.join(DOCS, p + '.html.new')
            if not os.path.exists(new):
                sys.exit('ERROR: 缺少 %s，先跑不帶 --apply 的生成' % new)
        for p in PAGES:
            os.replace(os.path.join(DOCS, p + '.html.new'), os.path.join(DOCS, p + '.html'))
            print('applied ' + os.path.join(DOCS, p + '.html'))
        return

    rows = load_rows()
    by_page = collections.OrderedDict((p, []) for p in PAGES)
    for r in rows:
        by_page[page_of(r)].append(r)

    # 第一遍：找出每卷的真實篇題
    heads = {}
    all_nums = []
    for p in PAGES:
        found = []
        for i, r in enumerate(by_page[p]):
            _lab, _src, shown, tr = pair_text(r)
            if not tr.strip():
                continue
            h = find_heading(shown, p)
            if h:
                found.append(dict(row=i, num=h[0], title=h[1], marker=h[2]))
                all_nums.append(h[0])
        heads[p] = found
    if all_nums != list(range(1, 31)):
        sys.exit('ERROR: 篇標題序列不符：%s' % all_nums)

    # 第二遍：補節（沒有篇題的卷）
    synth = {}
    last_num = 0
    for p in PAGES:
        if heads[p]:
            last_num = heads[p][-1]['num']
        else:
            if p == '上一上':
                synth[p] = dict(num=0, title='卷首')
            else:
                if last_num <= 0:
                    sys.exit('ERROR: %s 沒有篇題也無法判定續篇' % p)
                synth[p] = dict(num=last_num, title=None)

    # 同篇出現次數（含補節）→ 續篇標記
    totals = collections.Counter()
    for p in PAGES:
        for h in heads[p]:
            totals[h['num']] += 1
        if p in synth and synth[p]['num']:
            totals[synth[p]['num']] += 1

    occ = collections.Counter()
    labels = {}
    for p in PAGES:
        labs = []
        if p in synth:
            num = synth[p]['num']
            if num == 0:
                labs.append(('卷首', 'synth'))
            else:
                occ[num] += 1
                labs.append((CT.label(num, occ[num], totals[num]), 'synth'))
        for h in heads[p]:
            num = h['num']
            occ[num] += 1
            labs.append((CT.label(num, occ[num], totals[num]), h['row']))
        labels[p] = labs

    total_pairs = total_diagrams = 0
    all_skipped = []
    page_pairs = {}
    page_secs = {}

    for p in PAGES:
        rows_p = by_page[p]
        out = ['<h1>%s　%s</h1>' % (BOOK_TITLE, p),
               '<p class="byline">%s｜本卷：記文｜共 %d 段</p>' % (BYLINE, 0)]
        lab_by_row = {}
        secs = []
        syn_label = None
        for lab, ref in labels[p]:
            if ref == 'synth':
                syn_label = lab
            else:
                lab_by_row[ref] = lab
        if syn_label:
            secs.append(['p1', syn_label])
            out.append('<h2 class="sec" id="p1">%s</h2>' % html.escape(syn_label))
        pairs = 0
        diagrams = 0
        skipped = []
        used = set()
        for i, r in enumerate(rows_p):
            label, src, shown, tr = pair_text(r)
            if not tr.strip():
                skipped.append(r.get('key'))
                continue
            if i in lab_by_row:
                lab = lab_by_row[i]
                secs.append(['p%d' % (len(secs) + 1), lab])
                out.append('<h2 class="sec" id="p%d">%s</h2>'
                           % (len(secs), html.escape(lab)))
            pid = SA.uid('u', r.get('key'))
            if not pid:
                pid = ''
            base, n = pid, 1
            while pid and pid in used:
                n += 1
                pid = base + '-%d' % n
            if pid:
                used.add(pid)
            idattr = (' id="%s"' % pid) if pid else ''
            body_esc = fmt(shown)
            tr_esc = fmt(tr)
            if BOX.search(src):
                diagrams += 1
                out.append(
                    '<div class="pair j ko"%s><pre class="ko" style="white-space:pre;overflow-x:auto;'
                    'margin:0 0 .45rem;padding:.45rem .8rem;background:var(--ji-bg,#eef5f8);'
                    'border-left:3px solid var(--ji-border,#3f6f8f);color:var(--ji-fg,#1f4e6b);'
                    'font-size:13px;line-height:1.45;border-radius:0 4px 4px 0">'
                    '%s</pre><div class="t">%s</div></div>'
                    % (idattr, fmt_pre(shown), tr_esc))
            else:
                out.append('<div class="pair j"%s><div class="o ji">%s</div>'
                           '<div class="t">%s</div></div>'
                           % (idattr, body_esc, tr_esc))
            pairs += 1
        out[1] = ('<p class="byline">%s｜本卷：記文｜共 %d 段</p>'
                  % (BYLINE, pairs))
        if not secs:
            sys.exit('ERROR: %s 仍是 0 節' % p)

        i = PAGES.index(p)
        prev = PAGES[i - 1] if i > 0 else None
        nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
        page_html = SA.page(BOOK_TITLE + '　' + p, ''.join(out), prefix='../',
                            prev_url=(prev + '.html' if prev else None),
                            next_url=(nxt + '.html' if nxt else None),
                            prev_label=prev, next_label=nxt, current_label=p,
                            book_label=BOOK_TITLE, book_short='資持記',
                            pager=True, tools=True,
                            description='%s　%s：原文與白話逐段對照。' % (BOOK_TITLE, p))
        assert '<br><br>' not in page_html, p
        old_path = os.path.join(DOCS, p + '.html')
        io.open(old_path + '.new', 'w', encoding='utf-8', newline='\n').write(page_html)
        print('%s pairs=%d diagrams=%d secs=%d -> %s.new'
              % (p, pairs, diagrams, len(secs), old_path))

        total_pairs += pairs
        total_diagrams += diagrams
        all_skipped.extend(skipped)
        page_pairs[p] = pairs
        page_secs[p] = secs

    if total_pairs != 4157:
        sys.exit('ERROR: pair 數 %d，預期 4157（4182 筆 - 25 筆卷末校勘）' % total_pairs)
    if len(all_skipped) != 25:
        sys.exit('ERROR: 未譯筆數 %d，預期 25' % len(all_skipped))
    print('TOTAL pages=%d pairs=%d diagrams=%d headings=%d skipped=%d'
          % (len(PAGES), total_pairs, total_diagrams, len(all_nums), len(all_skipped)))
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
