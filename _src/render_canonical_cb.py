# -*- coding: utf-8 -*-
"""依 CBETA 卷題切頁，不用 row 的 vol 過濾；跨頁 row 以重疊方式選入。

2026-11-23 網站改善
-------------------
* 直接輸出完整頁面（頁尾／卷末導覽由 site_assets 產生，且在 `</main>` 之外）。
* 戒疏（jieshu）用既有 21 個卷題 marks 分節（每卷 4–6 節），不再一卷一標題。
* 篇名統一 `第N篇　短名`；跨卷續篇加 `（續）`／`（續一）`。
* 段別標籤只標原文欄；整卷只有一種段別時改在 byline 說明「本卷：鈔文」。
* 每個 pair 加由定稿 key 衍生的穩定 id（`u…`），搜尋錨點可分享、重建不漂移。
* 空譯不再靜默丟段：輸出 `.pair.missing` 並如實計數。
"""
import argparse
import html
import io
import json
import os
import re

import canon_titles as CT
import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')

BOOKS = {
    'xingshichao': dict(
        name='四分律刪繁補闕行事鈔', short='行事鈔',
        author='唐·道宣律師　撰',
        raw='TXT/01_四分律刪繁補闕行事鈔.txt',
        vols=('卷上', '卷中', '卷下'),
        pat=r'【四分律刪繁補闕行事鈔(卷[上中下](?:之[一二三四])?)】'),
    'jieshu': dict(
        name='四分律含注戒本疏行宗記', short='戒疏',
        author='唐·道宣律師　疏／宋·元照律師　記',
        raw='TXT/02_四分律含注戒本疏.txt',
        vols=('卷一', '卷二', '卷三', '卷四'),
        pat=r'【四分律含注戒本疏(?:行宗記)?(卷[一二三四](?:[上下])?之?[一二三四]?)】'),
    'yeshu': dict(
        name='四分律刪補隨機羯磨疏', short='業疏',
        author='唐·道宣律師　疏／宋·元照律師　記',
        raw='TXT/03_四分律刪補隨機羯磨疏.txt',
        vols=('卷一', '卷二', '卷三', '卷四'),
        pat=r'【四分律刪補隨機羯磨疏(?:濟緣記)?(卷[一二三四](?:之[一二三四])?)】'),
    'nicao': dict(
        name='四分比丘尼鈔', short='尼鈔',
        author='唐·道宣律師　述',
        raw='TXT/04_四分律比丘尼鈔.txt',
        vols=('卷上', '卷中', '卷下'),
        pat=r'【四分律比丘尼鈔(卷[上中下](?:之[上中下])?)】'),
    'yichao': dict(
        name='四分律拾毗尼義鈔', short='義鈔',
        author='唐·道宣律師　撰',
        raw='TXT/05_四分律拾毗尼義鈔.txt',
        vols=('卷上', '卷中'),
        pat=r'【四分律拾毗尼義鈔(卷[上中下](?:之[一二三四])?)】'),
}

LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')
PC = {'疏文': 's', '記文': 'j', '註文': 'z', '律文': 'lv', '序文': 'x', '鈔文': 'c'}
OC = {'疏文': 'shu', '記文': 'ji', '註文': 'zhu', '律文': 'lv', '序文': 'xu'}
PUNCT = re.compile(r'[，。；：！？、]')


def norm(v):
    m = re.match(r'卷([上中下]|[一二三四])', v)
    return '卷' + m.group(1) if m else v


def cn_num(s):
    vals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if s in vals:
        return vals[s]
    if s.startswith('十'):
        return 10 + vals.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十', 1)
        return vals.get(a, 0) * 10 + vals.get(b, 0)
    return 0


def fmt(s):
    s = html.escape(s)
    return re.sub(r'(?:\u3000{2,}|\n)+', '<br>', s)


def pick(src, disp):
    return disp if disp and PUNCT.search(disp) else src


def clean_tr(tr):
    """定稿譯文有時帶「【鈔文】」前綴；那是段別 metadata，不是譯文內容。"""
    return re.sub(r'^\s*(?:【(?:疏文|記文|鈔文|律文|註文|序文)】\s*)+', '', tr or '')


def pairs(row):
    segs = row.get('segments') or []
    if segs:
        return [((s.get('label') or '疏文').strip(),
                 pick(s.get('source', ''), s.get('display_source')),
                 clean_tr(s.get('translation'))) for s in segs]
    return [((row.get('label') or '疏文').strip(),
             pick(row.get('source', ''), row.get('display_source')),
             clean_tr(row.get('translation')))]


def section_label(book, mark, occ, total):
    """節標題顯示：戒疏保留卷題，其餘統一 `第N篇　短名（續）`。"""
    if mark == '卷首' or book == 'jieshu':
        return mark
    parsed = CT.parse_mark(mark)
    if not parsed:
        return mark
    n, short = parsed
    return '第%d篇　%s%s' % (n, short, CT.suffix(occ, total))


def build_section_marks(book, raw, hpos, body_start):
    marks = []
    if book == 'xingshichao':
        for m in re.finditer(r'(?m)^\s*(\d+)\s+([^\n(]+?篇)(?:\s*\([^\n)]*\))?\s*$', raw):
            if m.start() > body_start:
                marks.append((hpos[m.start()], '%s %s' % (m.group(1), m.group(2).strip())))
    elif book == 'nicao':
        for m in re.finditer(r'(?m)^○([^\n]{1,16}?篇)第([一二三四五六七八九十]+)\s*$', raw):
            if m.start() > body_start:
                marks.append((hpos[m.start()], '%d %s' % (cn_num(m.group(2)), m.group(1).strip())))
    elif book == 'yeshu':
        for m in re.finditer(r'(?m)^\s*([^\n]{1,16}?篇)第([一二三四五六七八九十]+)\s*$', raw):
            if m.start() > body_start:
                marks.append((hpos[m.start()], '%d %s' % (cn_num(m.group(2)), m.group(1).strip())))
    elif book == 'yichao':
        titles = ['毗尼大綱', '起戒差別', '十三難', '不學無知', '轉業變根', '破僧大意', '時非時',
                  '四波羅夷', '十三僧殘', '二不定', '三十捨墮', '九十單提', '四提舍尼', '眾學',
                  '七滅諍', '四諍']
        for i, t in enumerate(titles, 1):
            m = re.search(r'(?m)^' + re.escape(t) + r'\s*$', raw[body_start:])
            if m:
                marks.append((hpos[body_start + m.start()], '%d %s' % (i, t)))
    marks.sort()
    return marks


def chunk_of(raw_start, marks, default):
    ch = default
    for pos, label in marks:
        if raw_start >= pos:
            ch = label
        else:
            break
    return ch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', choices=sorted(BOOKS))
    ap.add_argument('--apply', action='store_true', help='把已產生的 .new 原子替換成 .html')
    args = ap.parse_args()

    todo = [args.book] if args.book else list(BOOKS)
    total_pairs = total_missing = 0
    print('BOOKS ' + ' '.join('%s=%s' % (b, BOOKS[b]['name']) for b in todo))

    for book in todo:
        cfg = BOOKS[book]
        name, short, author = cfg['name'], cfg['short'], cfg['author']
        raw = io.open(os.path.join(B, cfg['raw']), encoding='utf-8').read()
        hpos = [0] * (len(raw) + 1)
        c = 0
        for i, ch in enumerate(raw):
            if '\u4e00' <= ch <= '\u9fff':
                c += 1
            hpos[i + 1] = c

        marks = [(hpos[m.start()], norm(m.group(1)), m.group(1))
                 for m in re.finditer(cfg['pat'], raw)]
        starts = {}
        for pos, v, txt in marks:
            starts.setdefault(v, pos)
        order = [v for v in cfg['vols'] if v in starts]
        intervals = []
        for i, v in enumerate(order):
            a = starts[v]
            b = starts[order[i + 1]] if i + 1 < len(order) else len(raw)
            intervals.append((v, a, b))
        if intervals:
            intervals[0] = (intervals[0][0], 0, intervals[0][2])

        first = re.search(cfg['pat'], raw)
        body_start = first.start() if first else 0
        if book == 'jieshu':
            # 用 21 個卷題 marks 當節：每卷 4–6 節
            sec_marks = [(pos, txt) for pos, _v, txt in marks]
            per_vol_marks = {}
            for v, a, b in intervals:
                per_vol_marks[v] = [(p, t) for p, t in sec_marks if a <= p < b]
        else:
            per_vol_marks = None
            sec_marks = build_section_marks(book, raw, hpos, body_start)

        rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8')
                if x.strip()]
        rows = [r for r in rows if r.get('raw_start', -1) >= 0]
        rows.sort(key=lambda r: (r['raw_start'], r['raw_end']))

        # ── 第一遍：每卷節序，計算同篇出現次數（續篇標記） ──
        vol_rows = {}
        vol_chunks = {}
        chunk_counts = {}
        for v, a, b in intervals:
            sel = [r for r in rows if r['raw_start'] < b and r['raw_end'] > a]
            vol_rows[v] = sel
            if per_vol_marks is not None:
                local = per_vol_marks[v]
                chunks = []
                for r in sel:
                    ck = chunk_of(r['raw_start'], local, '卷首')
                    if not chunks or chunks[-1] != ck:
                        chunks.append(ck)
            else:
                chunks = []
                for r in sel:
                    ck = chunk_of(r['raw_start'], sec_marks, '卷首')
                    if not chunks or chunks[-1] != ck:
                        chunks.append(ck)
            vol_chunks[v] = chunks
            for ck in set(chunks):
                chunk_counts[ck] = chunk_counts.get(ck, 0) + 1

        # 每卷指派「第幾次出現」→ 顯示標題
        seen_occ = {}
        vol_display = {}
        for v, _a, _b in intervals:
            disp = {}
            for ck in vol_chunks[v]:
                if ck in disp:
                    continue
                seen_occ[ck] = seen_occ.get(ck, 0) + 1
                disp[ck] = section_label(book, ck, seen_occ[ck], chunk_counts.get(ck, 1))
            vol_display[v] = disp

        # ── 第二遍：輸出頁面 ──
        for v, a, b in intervals:
            sel = vol_rows[v]
            labels = set()
            for r in sel:
                for lab, _s, _t in pairs(r):
                    labels.add(lab if lab in LABELS else '疏文')
            show_labels = len(labels) > 1
            body = ['<h1>%s・%s</h1>' % (html.escape(name), html.escape(v))]
            pairs_n = 0
            missing = 0
            empty_src = 0
            used_ids = set()

            def make_id(key, seg_i):
                base = SA.uid('u', key, (seg_i + 1) if seg_i else '')
                if not base:
                    return ''
                cand, n = base, 1
                while cand in used_ids:
                    n += 1
                    cand = base + '-%d' % n
                used_ids.add(cand)
                return cand

            # 標籤政策：整卷只有一種段別 → 不逐段標，改 byline 說明
            byline = html.escape(author) + '｜略稱：' + html.escape(short)
            if not show_labels and labels:
                byline += '｜本卷：' + html.escape('、'.join(l for l in LABELS if l in labels))
            body.append('<p class="byline">%s｜共 %d 段</p>' % (byline, 0))

            last_ck = None
            sec_no = 0
            for r in sel:
                ck = chunk_of(r['raw_start'], per_vol_marks[v], '卷首') \
                    if per_vol_marks is not None else chunk_of(r['raw_start'], sec_marks, '卷首')
                if ck != last_ck:
                    # 戒疏：卷題前的書名／作者頁不另立「卷首」節，維持每卷 4–6 節
                    if not (book == 'jieshu' and ck == '卷首'):
                        sec_no += 1
                        body.append('<h2 class="sec" id="p%d">%s</h2>'
                                    % (sec_no, html.escape(vol_display[v].get(ck, ck))))
                    last_ck = ck
                for si, (lab, s, tr) in enumerate(pairs(r)):
                    lab = lab if lab in LABELS else '疏文'
                    if not s:
                        empty_src += 1
                        continue
                    pc, oc = PC.get(lab, ''), OC.get(lab, '')
                    ld = ('【%s】' % lab) if show_labels else ''
                    pid = make_id(r.get('key'), si)
                    idattr = (' id="%s"' % pid) if pid else ''
                    if not tr:
                        missing += 1
                        body.append('<div class="pair missing %s"%s>'
                                    '<div class="o %s">%s%s</div>'
                                    '<div class="t">（本段尚未白話）</div></div>'
                                    % (pc, idattr, oc, ld, fmt(s)))
                        continue
                    body.append('<div class="pair %s"%s><div class="o %s">%s%s</div>'
                                '<div class="t">%s</div></div>'
                                % (pc, idattr, oc, ld, fmt(s), fmt(tr)))
                    pairs_n += 1
            pairs_n += missing
            body[1] = '<p class="byline">%s｜共 %d 段</p>' % (byline, pairs_n)

            i = order.index(v)
            prev = order[i - 1] if i > 0 else None
            nxt = order[i + 1] if i + 1 < len(order) else None
            out = SA.page(name + '　' + v, ''.join(body), prefix='../',
                          prev_url=(prev + '.html' if prev else None),
                          next_url=(nxt + '.html' if nxt else None),
                          prev_label=prev, next_label=nxt, current_label=v,
                          book_label=name, book_short=short,
                          pager=True, tools=True,
                          description='%s　%s：原文與白話逐段對照。' % (name, v))
            page_path = os.path.join(B, 'docs', book, v + '.html')
            io.open(page_path + '.new', 'w', encoding='utf-8', newline='\n').write(out)
            total_pairs += pairs_n
            total_missing += missing
            print('%s %s pairs %d（篇 %d，未譯 %d，空原文 %d）-> %s.new'
                  % (short, v, pairs_n, len(vol_chunks[v]), missing, empty_src, page_path))

        if args.apply:
            for v, _a, _b in intervals:
                p = os.path.join(B, 'docs', book, v + '.html')
                os.replace(p + '.new', p)
                print('applied ' + p)

    print('TOTAL pairs %d missing %d' % (total_pairs, total_missing))


if __name__ == '__main__':
    main()
