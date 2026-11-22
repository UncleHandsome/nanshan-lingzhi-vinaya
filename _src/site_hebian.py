# -*- coding: utf-8 -*-
"""句級合編 → docs/hebian/*.html（來源：定稿/xingshichao.jsonl + 定稿/zhichi.jsonl）

重建原則
--------
* 原文、白話只讀 `定稿/*.jsonl`；不讀舊 HTML、不讀 docx。
* 12 卷、30 篇的卷篇結構依行事鈔分卷：卷界由 `TXT/01_…行事鈔.txt` 的
  卷題定位（漢字位移），不信任 jsonl 的 `chunk`（卷界常有 off-by-one）。
* 鈔／記對位沿用 `AI語譯/_work/hb_align.json`（舊合編的人工對位：記第 k 筆
  → 鈔第 c 段）；只用它決定「記文排在哪一段鈔文之後」，不取任何文字。
* 段落換行只輸出單一 `<br>`，寫檔前檢查不得出現 `<br><br>`。
* 卷末校勘異文串（zhichi 25 筆，有 skip_reason）不進正文。
"""
import bisect
import collections
import html
import io
import json
import os
import re
import sys

import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')
OUT = os.path.join(SITE, 'hebian')
C = os.path.join(B, '定稿')
os.makedirs(OUT, exist_ok=True)

HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
      '卷中之一', '卷中之二', '卷中之三', '卷中之四',
      '卷下之一', '卷下之二', '卷下之三', '卷下之四']
RAW = os.path.join(B, 'TXT', '01_四分律刪繁補闕行事鈔.txt')
VOL_RE = re.compile(r'四分律刪繁補闕行事鈔卷([上中下])之([一二三四])')
TITLE_RE = re.compile(r'^(.*?)篇第([一二三四五六七八九十]+)$')
SKIP_RE = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇(?:\([^)]*\))?$')
MARK_RE = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
HAN_RE = re.compile(r'[\u4e00-\u9fff]')
PUNCT = re.compile(r'[，。；：！？、]')
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
      '九': 9, '十': 10}
NAME2P = {
    '序': 0, '標宗': 0, '集僧': 1, '足數': 2, '受欲': 3, '羯磨': 4, '結界': 5,
    '僧網': 6, '受戒': 7, '師資': 8, '說戒': 9, '安居': 10, '自恣': 11,
    '篇聚': 12, '釋相': 13, '十三僧殘': 13, '持犯': 14, '懺六聚法': 15,
    '二衣': 16, '四藥': 17, '鉢器': 18, '對施': 19, '頭陀': 20, '僧像': 21,
    '訃請': 22, '導俗': 23, '主客': 24, '瞻病': 25, '諸雜': 26, '沙彌': 27,
    '尼眾': 28, '諸部': 29,
}
LABELS = ('鈔文', '記文', '疏文', '註文', '律文', '序文')


def han(s):
    return ''.join(HAN_RE.findall(s or ''))


def esc(s):
    return html.escape(s or '', quote=False)


def fmt(s):
    """原文／白話：只留單一 <br>，不得 <br><br>。"""
    s = (s or '').replace('\r\n', '\n').replace('\r', '\n')
    s = esc(s)
    s = re.sub(r'(?:\u3000{2,}|\n)+', '<br>', s)
    s = re.sub(r'(?:\s*<br>\s*)+', '<br>', s)
    return s.strip('<br>')


def strip_label(t):
    t = (t or '').strip()
    m = re.match(r'^【([^】]{1,4})】\s*\n?', t)
    if m and m.group(1) in LABELS:
        t = t[m.end():]
    return t.strip()


def clean_ji(s):
    """資持記細分檔把卷題／篇題夾在正文行內；顯示時把它們變成獨立一行。"""
    s = s or ''
    s = re.sub(r'四分律行事鈔資持記[上中下][一二三四]?[上中下]?', '', s)
    s = re.sub(r'(?:\d+\s*)?釋([\u4e00-\u9fff]{2,6})篇(?:\([^)）]*\))?',
               r'\n釋\1篇\n', s)
    s = re.sub(r'釋([\u4e00-\u9fff]{2,6})篇(?:\s*釋\1篇)+', r'釋\1篇', s)
    s = re.sub(r'\n{2,}', '\n', s)
    return s.strip()


def cn2int(s):
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + CN[s[1]]
    if '十' in s:
        a, b = s.split('十')
        return CN[a] * 10 + (CN[b] if b else 0)
    return CN[s]


def load_jsonl(book):
    return [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'),
                                          encoding='utf-8') if x.strip()]


def seg_units(row):
    """一個定稿單位可能有多段；每段一個 pair。"""
    segs = row.get('segments') or []
    if not segs:
        segs = [dict(label=row.get('label'), source=row.get('source'),
                     translation=row.get('translation'),
                     display_source=row.get('display_source'))]
    out = []
    for s in segs:
        src = s.get('display_source') or s.get('source') or ''
        if not src:
            src = row.get('display_source') or row.get('source') or ''
        out.append(dict(label=s.get('label') or row.get('label') or '',
                        source=src,
                        translation=strip_label(s.get('translation') or
                                                row.get('translation'))))
    return out


def volume_bounds():
    hraw = han(io.open(RAW, encoding='utf-8').read())
    starts = {}
    for m in VOL_RE.finditer(hraw):
        starts.setdefault('卷%s之%s' % (m.group(1), m.group(2)), m.start())
    missing = [v for v in HB if v not in starts]
    if missing:
        raise SystemExit('卷題定位失敗：%s' % missing)
    bounds = []
    for i, v in enumerate(HB):
        a = starts[v]
        b = starts[HB[i + 1]] if i + 1 < len(HB) else len(hraw)
        bounds.append((v, a, b))
    return hraw, bounds


def volume_of(pos, bounds):
    for v, a, b in bounds:
        if a <= pos < b:
            return v
    return HB[0] if pos < bounds[0][1] else HB[-1]


def old_chao_sections():
    """重現舊會本 30 篇的鈔段落文字（只用來定位，不取譯文）。"""
    d = os.path.join(B, 'TXT_分卷', '01_行事鈔')
    pat = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
    pat2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
    secs, cur = [], None
    for f in sorted(os.listdir(d), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        for line in io.open(os.path.join(d, f), encoding='utf-8').read().split('\n')[5:]:
            o = line.strip()
            if not o or pat2.match(o):
                continue
            m = pat.match(o)
            if m:
                n = cn2int(m.group(2))
                cur = next((x for x in secs if x['no'] == n), None)
                if cur is None:
                    cur = dict(name=m.group(1), no=n, items=[])
                    secs.append(cur)
                continue
            if cur is not None:
                cur['items'].append(o)
    secs.sort(key=lambda x: x['no'])
    return secs


def item_spans(sections, hraw):
    """舊鈔段落 → raw 漢字區間；先全文，再前綴退避，最後內插。"""
    spans, ptr = [], 0
    for sec in sections:
        for o in sec['items']:
            t = han(o)
            j = hraw.find(t, ptr)
            if j < 0:
                j = hraw.find(t)
            if j < 0:
                for L in (40, 30, 20, 16, 12, 10):
                    k = hraw.find(t[:L], ptr)
                    if k < 0:
                        k = hraw.find(t[:L])
                    if k >= 0:
                        j = k
                        break
            spans.append((j, j + len(t)) if j >= 0 else None)
            if j >= 0:
                ptr = j
    for i, sp in enumerate(spans):
        if sp is not None:
            continue
        prev = next((spans[k] for k in range(i - 1, -1, -1) if spans[k]), None)
        nxt = next((spans[k] for k in range(i + 1, len(spans)) if spans[k]), None)
        if prev and nxt:
            a, b = prev[1], max(prev[1] + 1, nxt[0])
        elif prev:
            a, b = prev[1], prev[1] + 1
        elif nxt:
            a, b = max(0, nxt[0] - 1), nxt[0]
        else:
            a = b = 0
        spans[i] = (a, b)
    return spans


def pair_html(u, kind, sid):
    label = u.get('label') or ('鈔文' if kind == '鈔' else '記文')
    cls = 'o' if kind == '鈔' else 'o2'
    return ('<div class="pair" id="s%d"><div class="%s">【%s】%s</div>'
            '<div class="t">%s</div></div>'
            % (sid, cls, esc(label), fmt(u['source']), fmt(u['translation'])))


def main():
    hraw, bounds = volume_bounds()
    xs = load_jsonl('xingshichao')
    zc = load_jsonl('zhichi')

    # ---- 篇題：同一篇號取最後一筆（前面的是卷首目次） ----
    actual = {}
    title_ids = set()
    seen_author = False
    for r in xs:
        src = (r.get('source') or '').strip()
        if src == '京兆崇義寺沙門釋道宣撰述':
            if seen_author:
                title_ids.add(id(r))   # 卷中／卷下卷首重複的作者題記
                continue
            seen_author = True
        if SKIP_RE.match(src):
            title_ids.add(id(r))
            continue
        m = TITLE_RE.match(src)
        if not m or len(src) >= 30:
            continue
        title_ids.add(id(r))
        actual[cn2int(m.group(2))] = (m.group(1), r)
    title_pos = sorted((r.get('raw_start', 0), n) for n, (_, r) in actual.items())
    tpos = [x[0] for x in title_pos]
    if len(actual) != 30:
        raise SystemExit('篇題不足 30：%d' % len(actual))

    # ---- 鈔：分篇、分卷 ----
    chao = []
    for r in sorted(xs, key=lambda x: (x.get('raw_start', 0), x.get('raw_end', 0))):
        if id(r) in title_ids:
            continue
        pos = r.get('raw_start', 0)
        k = bisect.bisect_right(tpos, pos) - 1
        ch = title_pos[k][1] if k >= 0 else 0
        vol = volume_of(pos, bounds)
        end = r.get('raw_end', pos + len(han(r.get('source'))))
        for u in seg_units(r):
            chao.append(dict(chapter=ch, vol=vol, pos=pos, end=end,
                             label=u['label'], source=u['source'],
                             translation=u['translation']))
    chap_vols = collections.defaultdict(list)
    for u in chao:
        if u['chapter'] and u['vol'] not in chap_vols[u['chapter']]:
            chap_vols[u['chapter']].append(u['vol'])

    # ---- 記：依「釋X篇」切篇；單元若在篇界夾帶前篇尾巴，拆成兩筆 ----
    zrows = [r for r in sorted(zc, key=lambda x: int(re.sub(r'\D', '', str(x.get('key'))) or 0))
             if not (r.get('skip_reason') or '').strip()]
    zi = collections.defaultdict(list)
    tails = []
    cur = 0
    for r in zrows:
        raw_src = r.get('display_source') or r.get('source') or ''
        tr = strip_label(r.get('translation'))
        m = MARK_RE.search(raw_src)
        if m and m.group(1) in NAME2P:
            new = NAME2P[m.group(1)]
            pre = raw_src[:m.start()]
            pre = re.sub(r'四分律行事鈔資持記[上中下][一二三四]?[上中下]?', '', pre)
            pre = re.sub(r'\d+\s*$', '', pre).strip()
            if new != cur and len(han(pre)) > 4:
                paras = re.split(r'\n\s*\n', tr)
                j = next((k for k in range(1, len(paras))
                          if m.group(1) in paras[k] and '篇' in paras[k]), None)
                if j:
                    tails.append((cur, dict(label='記文',
                                            source=pre.strip('，。；、 '),
                                            translation='\n\n'.join(paras[:j]))))
                    tr = '\n\n'.join(paras[j:])
                    raw_src = raw_src[m.start():]
            cur = new
        zi[cur].append(dict(label=r.get('label') or '記文',
                            source=clean_ji(raw_src),
                            translation=tr))
    if len(zi[11]) > 90:
        zi[12].insert(0, zi[11].pop())
    if len(zi[29]) > 28:
        zi[29] = zi[29][:28]

    # ---- 舊鈔段落 → 新鈔 unit ----
    secs = old_chao_sections()
    if len(secs) != 30:
        raise SystemExit('舊會本不是 30 篇：%d' % len(secs))
    spans = item_spans(secs, hraw)
    unit_last = {}
    k = 0
    for p, sec in enumerate(secs):
        for ci, o in enumerate(sec['items']):
            a, b = spans[k]
            k += 1
            cand = [i for i, u in enumerate(chao)
                    if u['chapter'] == p + 1 and u['pos'] < b and u['end'] > a]
            if not cand:
                cand = [i for i, u in enumerate(chao)
                        if u['chapter'] == p + 1 and u['pos'] >= a][:1]
            if not cand:
                cand = [i for i, u in enumerate(chao) if u['chapter'] == p + 1][-1:]
            if cand:
                unit_last[(p + 1, ci + 1)] = max(cand)

    # ---- 記 → 錨點 ----
    AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'),
                           encoding='utf-8'))
    after = collections.defaultdict(list)
    pre = collections.defaultdict(list)
    miss_align = 0
    extra_misalign = 0
    for p in range(30):
        zlist = zi[p]
        am = AM.get(str(p), [])
        n_items = len(secs[p]['items'])
        prev = 0
        if len(am) != len(zlist):
            extra_misalign += abs(len(am) - len(zlist))
        for k2, z in enumerate(zlist):
            c = am[k2] if k2 < len(am) else (am[-1] if am else 0)
            c = max(prev, min(int(c), n_items))
            prev = c
            if c == 0:
                pre[p].append(z)
            elif (p + 1, c) in unit_last:
                after[unit_last[(p + 1, c)]].append(z)
            else:
                miss_align += 1
                pre[p].append(z)

    # 篇界尾巴：接在該篇最後一個鈔 unit 的記文之後
    last_unit = {}
    for ui, u in enumerate(chao):
        last_unit[u['chapter']] = ui
    tail_count = 0
    for p, t in tails:
        # p=0 是「序＋標宗」合併：尾巴屬標宗，接在第 1 篇最後一個鈔 unit
        target = 1 if p == 0 else p
        if target in last_unit:
            after[last_unit[target]].append(t)
            tail_count += 1
        else:
            pre[p].append(t)

    # ---- 輸出 ----
    stats = dict(vols=0, sections=0, pairs=0, chao=0, ji=0,
                 missing_spans=sum(1 for s in spans if s is None),
                 miss_align=miss_align, misalign_count=extra_misalign,
                 tails=tail_count, br2=0)
    entries = []
    emitted_pre = set()
    nav_vols = []
    for vi, vol in enumerate(HB):
        body, toc = [], []
        secno = 0
        cur_ch = None
        units = [ui for ui, u in enumerate(chao) if u['vol'] == vol]
        sid = 0

        def emit_zi(z):
            nonlocal sid
            if not han(z['source']):
                return
            sid += 1
            body.append(pair_html(z, '記', sid))
            entries.append(dict(v=vol, o='【%s】%s' % (z['label'], z['source']),
                                t=z['translation'], i='s%d' % sid))
            stats['ji'] += 1
            stats['pairs'] += 1

        for ui in units:
            u = chao[ui]
            ch = u['chapter']
            if ch != cur_ch:
                # 卷首（序）的記文：接在卷首鈔文之後、第1篇之前
                if cur_ch == 0 and 0 not in emitted_pre:
                    for z in pre.get(0, []):
                        emit_zi(z)
                    emitted_pre.add(0)
                cur_ch = ch
                secno += 1
                if ch == 0:
                    title = '卷首'
                else:
                    title = '第%d篇　%s' % (ch, actual[ch][0])
                    if chap_vols[ch][0] != vol:
                        title += '（續）'
                toc.append((secno, title))
                body.append('<h2 class="sec" id="p%d">%s</h2>' % (secno, esc(title)))
            if ch != 0 and ch not in emitted_pre and pre.get(ch):
                for z in pre[ch]:
                    emit_zi(z)
                emitted_pre.add(ch)
            sid += 1
            body.append(pair_html(u, '鈔', sid))
            entries.append(dict(v=vol, o='【%s】%s' % (u['label'], u['source']),
                                t=u['translation'], i='s%d' % sid))
            stats['chao'] += 1
            stats['pairs'] += 1
            for z in after.get(ui, []):
                emit_zi(z)
        if not body:
            raise SystemExit('%s 沒有內容' % vol)
        prev = HB[vi - 1] if vi > 0 else None
        nxt = HB[vi + 1] if vi + 1 < len(HB) else None
        pager = ''
        if prev:
            pager += '<a href="%s.html">← %s</a>' % (prev, esc(prev))
        if nxt:
            pager += '<a href="%s.html">%s →</a>' % (nxt, esc(nxt))
        ttl = '四分律行事鈔資持記　句級合編　' + vol
        body_html = ('<h1>' + esc(ttl) + '</h1>'
                     '<p class="byline">鈔文（淺褐）與記文（淺藍）逐段並列，每段附白話；'
                     '原文、白話皆取自定稿 JSONL。</p>'
                     + '\n'.join(body)
                     + '<div class="pager">' + pager + '</div>')
        out = SA.page(ttl, body_html, prefix='../',
                      prev_url=(prev + '.html' if prev else None),
                      next_url=(nxt + '.html' if nxt else None),
                      prev_label=prev, next_label=nxt, current_label=vol)
        if '<br><br>' in out:
            stats['br2'] += out.count('<br><br>')
        io.open(os.path.join(OUT, vol + '.html'), 'w', encoding='utf-8').write(out)
        stats['vols'] += 1
        stats['sections'] += len(toc)
        nav_vols.append(dict(v=vol, secs=[['p%d' % n, t] for n, t in toc]))
        print(vol, '篇', len(toc), 'pair', sid, flush=True)

    # 搜尋索引：由剛寫出的頁面重建，anchor 一定對得上（build_search_index.py）
    import build_search_index as BSI
    BSI.build(site=SITE, only=['hebian'], quiet=True)

    # 只更新 nav.json 的 hebian 段，其他書不動（避免蓋掉別人的重建）
    np = os.path.join(SITE, 'nav.json')
    nav = json.load(io.open(np, encoding='utf-8'))
    for b in nav.get('books', []):
        if b.get('out') == 'hebian':
            b['vols'] = nav_vols
            break
    tmp = np + '.tmp'
    io.open(tmp, 'w', encoding='utf-8').write(
        json.dumps(nav, ensure_ascii=False, indent=1) + '\n')
    os.replace(tmp, np)

    if stats['br2']:
        raise SystemExit('出現 <br><br>：%d' % stats['br2'])
    print(json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == '__main__':
    main()
