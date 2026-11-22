# -*- coding: utf-8 -*-
"""句級合編 → docs/hebian/*.html（來源：定稿/xingshichao.jsonl + 定稿/zhichi.jsonl）

2026-11-22 重寫對齊規則
------------------------
* 以「篇」為硬邊界：《行事鈔》篇題（取正文那一筆，不取卷首目次）與《資持記》
  `釋○篇` 標題同時作錨，記文不得跨篇。
* `釋○篇` 常夾在上一篇記文末尾（同一記段前半是上一篇尾巴、後半才是新篇）。
  本版依標題把該段切成「前篇尾巴」與「新篇開頭」兩筆，白話依段落標題切分；
  找不到標題段時才依原文長度比例切，不再整段塞給下一篇。
* 卷首：元照自序／標五例維持純記文；`釋序題`、`釋序文` 起與鈔序逐段對插。
* 鈔／記对位：沿用 `hb_align.json` 的舊段號，映射到新版鈔段；再以記文開頭
  的牒詞（前 2–8 字）在鄰近 ±2 鈔段內校正「記先鈔後」。
* 輸出前清掉 `---`、`（出處：…）`、`■ 鈔文`、卷題殘留。
"""
import bisect
import collections
import html
import io
import json
import os
import re

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
OLD_WORK = os.path.join(B, 'AI語譯', '_work', 'hb_align.json')
ARC_WORK = os.path.join(os.path.dirname(B), '三大部_ARCHIVE_20261122',
                        'AI語譯', '_work', 'hb_align.json')
VOL_RE = re.compile(r'四分律刪繁補闕行事鈔卷([上中下])之([一二三四])')
TITLE_RE = re.compile(r'^(.*?)篇第([一二三四五六七八九十]+)$')
SKIP_RE = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇(?:\([^)]*\))?$')
MARK_RE = re.compile(r'釋([\u4e00-\u9fff]{1,6}?)(篇|題|文)')
HAN_RE = re.compile(r'[\u4e00-\u9fff]')
CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8,
      '九': 9, '十': 10}
NAME2P = {
    '標宗': 1, '集僧': 2, '足數': 3, '受欲': 4, '羯磨': 5, '結界': 6,
    '僧網': 7, '受戒': 8, '師資': 9, '說戒': 10, '安居': 11, '自恣': 12,
    '篇聚': 13, '釋相': 14, '持犯': 15, '懺六聚法': 16, '二衣': 17,
    '四藥': 18, '鉢器': 19, '對施': 20, '頭陀': 21, '僧像': 22, '訃請': 23,
    '導俗': 24, '主客': 25, '瞻病': 26, '諸雜': 27, '沙彌': 28, '尼眾': 29,
    '諸部': 30,
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


def strip_vol_titles(s):
    """只刪卷題『詞』，不刪同一行的正文。"""
    s = re.sub(r'(?m)^[ \t]*《四分律行事鈔資持記》[^\n]{0,24}$', '', s)
    s = re.sub(r'《四分律行事鈔資持記》\s*卷?[上中下]?[一二三四]?[上中下]?終?', '', s)
    s = re.sub(r'四分律行事鈔資持記\s*卷?[上中下]?[一二三四]?[上中下]?終?', '', s)
    s = re.sub(r'大宋餘杭沙門釋元照撰[^\n。]*?卷題號[^\n。]*。?', '', s)
    s = re.sub(r'(?m)^[ \t]*卷題號[^\n]*$', '', s)
    s = re.sub(r'注撰，注宜作著。', '', s)
    s = s.replace('（並含序文）', '').replace('(並含序文)', '')
    return s


def clean_tr(s):
    """白話同樣清掉補丁標記；不刪正文。"""
    s = strip_label(s)
    s = re.sub(r'(?m)^\s*-{3,}\s*$', '', s)
    s = re.sub(r'（\s*出處\s*[:：][^）]*）', '', s)
    s = re.sub(r'\(\s*出處\s*[:：][^)]*\)', '', s)
    s = re.sub(r'■\s*(?:鈔文|記文|疏文|註文|律文|序文)', '', s)
    s = strip_vol_titles(s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    return s.strip()


def clean_text(s):
    """清掉卷題、補丁標記、出處行；保留〔夾注〕。"""
    s = (s or '').replace('\r\n', '\n').replace('\r', '\n')
    s = s.replace('\ufeff', '')
    s = re.sub(r'(?m)^\s*-{3,}\s*$', '', s)
    s = re.sub(r'（\s*出處\s*[:：][^）]*）', '', s)
    s = re.sub(r'\(\s*出處\s*[:：][^)]*\)', '', s)
    s = re.sub(r'■\s*(?:鈔文|記文|疏文|註文|律文|序文)', '', s)
    s = strip_vol_titles(s)
    s = re.sub(r'釋([\u4e00-\u9fff]{1,6})篇\([^)]*\)', r'釋\1篇', s)
    s = re.sub(r'(?<![0-9])[0-9]+\s*(?=釋[\u4e00-\u9fff]{1,6}篇)', '', s)
    s = re.sub(r'^\s*\d+\s*釋[\u4e00-\u9fff]{1,6}篇(?:\([^)]*\))?\s*$', '', s, flags=re.M)
    s = re.sub(r'\s*\d+\s*$', '', s)
    s = strip_vol_titles(s)
    s = s.replace('〔并序〕', '').replace('(并序)', '')
    s = re.sub(r'撰序序', '撰\n序\n', s)
    s = re.sub(r'^(釋[\u4e00-\u9fff]{1,6}(?:篇|題|文))\1', r'\1', s)
    s = re.sub(r'[ \t]+\n', '\n', s)
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
                        source=clean_text(src),
                        translation=clean_tr(s.get('translation') or
                                             row.get('translation'))))
    return [x for x in out if han(x['source'])]


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
    """舊會本 30 篇的鈔段落文字（只用來定位，不取譯文）。"""
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


def load_align():
    for p in (OLD_WORK, ARC_WORK):
        if os.path.exists(p):
            return json.load(io.open(p, encoding='utf-8'))
    return {}


def para_heading(name, kind):
    """判斷某個白話段落是否為「釋○篇」標題段。"""
    def ok(p):
        p = p.strip()
        if not p or len(p) > 90:
            return False
        if kind == '題':
            return (p.startswith('解釋序題') or p.startswith('釋序題')
                    or ('釋序題' in p[:16]) or ('序題' in p and len(p) <= 40))
        if kind == '文':
            return (p.startswith('以下解釋序文') or p.startswith('解釋序文')
                    or p.startswith('釋序文') or ('釋序文' in p[:16])
                    or ('序文' in p and len(p) <= 40))
        if p.startswith('第') and '篇' in p[:40] and name in p[:40]:
            return True
        if '釋%s' % name in p[:24] and '篇' in p[:40]:
            return True
        return bool(re.search(r'〈?%s[^〉]{0,4}篇〉?' % re.escape(name), p[:40]))
    return ok


def split_marker(row, name, kind):
    """把夾帶 `釋○篇` 的記段切成 (前篇尾巴, 新篇開頭)。

    kind: '篇' / '題' / '文'
    """
    ds = row.get('display_source') or row.get('source') or ''
    if kind == '篇':
        pat = re.compile(r'釋%s篇' % re.escape(name))
    else:
        pat = re.compile(r'釋%s' % re.escape(name))
    m = pat.search(ds)
    if not m:
        return None
    pre_raw, head_raw = ds[:m.start()], ds[m.start():]
    pre, head = clean_text(pre_raw), clean_text(head_raw)
    tr = clean_tr(row.get('translation'))
    paras = [x for x in re.split(r'\n\s*\n', tr) if x.strip()]
    idx = None
    for i, p in enumerate(paras):
        if para_heading(name, kind)(p):
            idx = i
            break
    if idx is not None:
        tail_tr = '\n\n'.join(paras[:idx]).strip()
        head_tr = '\n\n'.join(paras[idx:]).strip()
    else:
        # 依原文長度比例找最接近的段落界
        ratio = len(han(pre)) / max(1, len(han(ds)))
        target = len(tr) * ratio
        acc, best, bidx = 0, 1e9, 0
        for i, p in enumerate(paras):
            if abs(acc - target) < best:
                best, bidx = abs(acc - target), i
            acc += len(p)
        tail_tr = '\n\n'.join(paras[:bidx]).strip()
        head_tr = '\n\n'.join(paras[bidx:]).strip()
    return pre, tail_tr, head, head_tr


def build_chao(xs, hraw, bounds):
    """鈔：以正文篇題作硬邊界（同篇號取 raw_start 最大者）。"""
    titles = {}
    for r in xs:
        src = (r.get('source') or '').strip()
        m = TITLE_RE.match(src)
        if not m or len(src) >= 30:
            continue
        n = cn2int(m.group(2))
        pos = r.get('raw_start') or 0
        if n not in titles or pos > titles[n][0]:
            titles[n] = (pos, m.group(1), r)
    if len(titles) != 30:
        raise SystemExit('篇題不足 30：%d' % len(titles))
    title_ids = set()
    for r in xs:
        src = (r.get('source') or '').strip()
        if TITLE_RE.match(src) or SKIP_RE.match(src):
            title_ids.add(id(r))
    # 卷首的重複作者題記只留第一筆
    seen_author = False
    for r in xs:
        if (r.get('source') or '').strip() == '京兆崇義寺沙門釋道宣撰述':
            if seen_author:
                title_ids.add(id(r))
            seen_author = True
    tpos = sorted((v[0], n) for n, v in titles.items())
    tstart = [x[0] for x in tpos]
    chao = []
    for r in sorted(xs, key=lambda x: (x.get('raw_start') or 0, x.get('raw_end') or 0)):
        if id(r) in title_ids:
            continue
        pos = r.get('raw_start') or 0
        k = bisect.bisect_right(tstart, pos) - 1
        ch = tpos[k][1] if k >= 0 else 0
        vol = volume_of(pos, bounds)
        end = r.get('raw_end') or pos + len(han(r.get('source')))
        for u in seg_units(r):
            chao.append(dict(chapter=ch, vol=vol, pos=pos, end=end,
                             label=u['label'], source=u['source'],
                             translation=u['translation']))
    return chao, titles


def build_ji(zc):
    """記：依 `釋○篇` 硬錨切篇；回傳 (units, anchors)。

    每個 unit: ch(0=卷首, 1..30=篇), sub('自序'/'序題'/'序文'/''),
               part('body'/'tail'/'head'), row(原 jsonl 索引)
    """
    zrows = sorted([r for r in zc if not (r.get('skip_reason') or '').strip()],
                   key=lambda x: int(re.sub(r'\D', '', str(x.get('key'))) or 0))
    ji, anchors = [], []
    cur_ch, in_shou, cur_sub = 0, True, '自序'

    def add(ch, sub, part, row, src, tr):
        if han(src):
            ji.append(dict(ch=ch, sub=sub, part=part, row=row,
                           source=src, translation=tr))

    for ri, r in enumerate(zrows):
        ds = r.get('display_source') or r.get('source') or ''
        m = None
        for _m in MARK_RE.finditer(ds):
            if _m.group(2) == '篇' and _m.group(1) in NAME2P:
                if '沙門' in ds[max(0, _m.start() - 3):_m.start()]:
                    continue
                m = _m
                break
            if _m.group(2) in ('題', '文') and in_shou and _m.group(1) == '序':
                m = _m
                break
        if m and m.group(2) == '篇' and m.group(1) in NAME2P:
            name = m.group(1)
            new = NAME2P[name]
            sp = split_marker(r, name, '篇')
            if sp is None:
                add(cur_ch, cur_sub, 'body', ri, clean_text(ds),
                    clean_tr(r.get('translation')))
                continue
            pre, tail_tr, head, head_tr = sp
            # 前篇尾巴（卷題號／卷末字樣屬卷題，不歸前篇）
            if han(pre) and not re.search(r'卷題號|卷[上中下]?[一二三四]?終',
                                          ds[:m.start()]):
                add(cur_ch, cur_sub, 'tail', ri, pre, tail_tr)
            # 新篇開頭
            if in_shou and cur_sub == '序文':
                # 釋標宗篇：卷首尾巴已存，開頭進標宗
                pass
            in_shou = False
            cur_ch, cur_sub = new, ''
            add(cur_ch, cur_sub, 'head', ri, head, head_tr)
            anchors.append(dict(name=name, ch=new, row=ri, pre_han=len(han(pre)),
                                head_han=len(han(head)), display=ds))
        elif m and m.group(2) in ('題', '文') and in_shou:
            kind = m.group(2)
            name = m.group(1)
            sp = split_marker(r, name, kind)
            if sp is None:
                add(0, cur_sub, 'body', ri, clean_text(ds),
                    clean_tr(r.get('translation')))
                continue
            pre, tail_tr, head, head_tr = sp
            if han(pre):
                add(0, cur_sub, 'tail', ri, pre, tail_tr)
            cur_sub = '序題' if kind == '題' else '序文'
            add(0, cur_sub, 'head', ri, head, head_tr)
            anchors.append(dict(name='序' + ('題' if kind == '題' else '文'),
                                ch=0, row=ri, pre_han=len(han(pre)),
                                head_han=len(han(head)), display=ds))
        else:
            add(cur_ch, cur_sub, 'body', ri, clean_text(ds),
                clean_tr(r.get('translation')))
    return ji, anchors


def unit_last_map(secs, spans, chao):
    unit_last = {}
    k = 0
    for p, sec in enumerate(secs):
        for ci, _ in enumerate(sec['items']):
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
    return unit_last


def refine_anchor(base, src, chao, i0, i1):
    """用記文開頭牒詞在 base±2 內找更合適的鈔段。"""
    z = han(src)
    if not z:
        return base
    best, bestL = base, 0
    lo = max(i0, base - 2)
    hi = min(i1, base + 2)
    for j in range(lo, hi + 1):
        cj = han(chao[j]['source'])
        L = 0
        for L in range(min(8, len(z)), 1, -1):
            if z[:L] in cj:
                break
        else:
            L = 0
        if L > bestL or (L == bestL and L and abs(j - base) < abs(best - base)):
            bestL, best = L, j
    return best if bestL >= 2 else base


def proportional_anchor(k, n, i0, i1):
    if n <= 0:
        return i0
    return i0 + min(i1 - i0, int((k + 0.5) * (i1 - i0 + 1) / n))


MANUAL_ANCHOR = {
    # 科文已明指下一鈔，舊段號卻掛在前一鈔：以鈔文首句硬錨
    (1, 380): '四明戒相者',
}


def align_ji(ji, chao, unit_last, AM):
    """回傳 anchor: list of (anchor_index or -1 for pre, ji unit)。"""
    by_ch = collections.defaultdict(list)
    for i, u in enumerate(ji):
        by_ch[u['ch']].append(i)
    anchors = []
    # ---- 卷首 ----
    shou = [i for i, u in enumerate(chao) if u['chapter'] == 0]
    shou_ji = by_ch.get(0, [])
    # 依 sub 分組
    for sub in ('自序', '序題', '序文'):
        ids = [i for i in shou_ji if ji[i]['sub'] == sub]
        if sub == '自序':
            for i in ids:
                anchors.append((-1, i))
        elif sub == '序題':
            # 序題：鈔 2（序題）；撰述：鈔 3
            cut = next((k for k, i in enumerate(ids)
                        if han(ji[i]['source']).startswith('京者')), len(ids))
            for k, i in enumerate(ids):
                if k < cut:
                    anchors.append((shou[2] if len(shou) > 2 else shou[-1], i))
                else:
                    anchors.append((shou[3] if len(shou) > 3 else shou[-1], i))
        else:
            # 序文：前段用固定列錨（記 row），其後按長度比例分到鈔 11 之後
            fixed = [(50, 4), (78, 5), (86, 6), (92, 7), (112, 8), (116, 9), (125, 10)]
            rows = [(ji[i]['row'], i) for i in ids]
            for k, (row, i) in enumerate(rows):
                target = None
                for rr, cidx in fixed:
                    if row >= rr:
                        target = cidx
                if target is None:
                    target = 4
                # row >= 125 後改比例
                if row >= 125 and len(shou) > 11:
                    rest = [(rr, ii) for rr, ii in rows if rr >= 125]
                    pos = next(j for j, (rr, _) in enumerate(rest) if rr == row)
                    target = 11 + int(pos * (len(shou) - 11) / max(1, len(rest)))
                anchors.append((shou[min(target, len(shou) - 1)], i))
    # ---- 各篇 ----
    for ch in range(1, 31):
        ids = by_ch.get(ch, [])
        if not ids:
            continue
        cidx = [i for i, u in enumerate(chao) if u['chapter'] == ch]
        if not cidx:
            continue
        i0, i1 = cidx[0], cidx[-1]
        am = [int(x) for x in AM.get(str(ch - 1), [])]
        maxc = max(am) if am else 0
        # 篇1：舊 hb_align 漏掉第4段（戒體），用 pian_bounds 的 16 個段界修正
        b1 = None
        if ch == 1:
            first = min(ji[i]['row'] for i in ids)
            b1 = [(2, 19), (3, 27), (4, 30), (5, 35), (6, 38), (7, 39),
                  (8, 41), (9, 42), (10, 46), (11, 55), (12, 64),
                  (13, 76), (14, 77), (15, 88), (16, 101)]
            b1 = [(c, first + off) for c, off in b1]
        # 本篇原始 row 順序 → hb_align 序號
        rows = sorted({ji[i]['row'] for i in ids})
        row2k = {r: k for k, r in enumerate(rows)}
        base = {}
        for i in ids:
            u = ji[i]
            if u['part'] == 'tail':
                base[i] = i1
                continue
            k = row2k.get(u['row'], 0)
            if b1:
                c = 1
                for cc, rr in b1:
                    if u['row'] >= rr:
                        c = cc
            else:
                c = am[k] if k < len(am) else 0
            if c <= 0:
                base[i] = i0
            else:
                b = unit_last.get((ch, c))
                if b is None:
                    if maxc > 0:
                        b = cidx[min(len(cidx) - 1,
                                     int((c - 0.5) * len(cidx) / maxc))]
                    else:
                        b = cidx[min(len(cidx) - 1,
                                     int(k * len(cidx) / max(1, len(ids))))]
                base[i] = b
            _mt = MANUAL_ANCHOR.get((ch, u['row']))
            if _mt:
                for _j in cidx:
                    if chao[_j]['source'].startswith(_mt):
                        base[i] = _j
                        break
        # 單調 + 牒詞校正
        last = i0
        for i in sorted(ids, key=lambda x: (ji[x]['row'], 0 if ji[x]['part'] != 'head' else 1)):
            u = ji[i]
            b = max(last, base[i])
            if u['part'] == 'tail':
                b = i1
            elif u['source'] and b >= i0:
                b = refine_anchor(b, u['source'], chao, i0, i1)
            b = max(last, min(b, i1))
            last = b
            anchors.append((b, i))
    return anchors


def emit_pair(u, kind, sid):
    label = u.get('label') or ('鈔文' if kind == '鈔' else '記文')
    cls = 'o' if kind == '鈔' else 'o2'
    return ('<div class="pair" id="s%d"><div class="%s">【%s】%s</div>'
            '<div class="t">%s</div></div>'
            % (sid, cls, esc(label), fmt(u['source']), fmt(u['translation'])))


def main():
    hraw, bounds = volume_bounds()
    xs = load_jsonl('xingshichao')
    zc = load_jsonl('zhichi')
    chao, titles = build_chao(xs, hraw, bounds)
    ji, anchors = build_ji(zc)
    AM = load_align()

    chap_vols = collections.defaultdict(list)
    for u in chao:
        if u['chapter'] and u['vol'] not in chap_vols[u['chapter']]:
            chap_vols[u['chapter']].append(u['vol'])

    secs = old_chao_sections()
    if len(secs) != 30:
        raise SystemExit('舊會本不是 30 篇：%d' % len(secs))
    spans = item_spans(secs, hraw)
    unit_last = unit_last_map(secs, spans, chao)

    pairs = align_ji(ji, chao, unit_last, AM)
    by_anchor = collections.defaultdict(list)
    anchored = set()
    for a, i in pairs:
        by_anchor[a].append(i)
        anchored.add(i)

    stats = dict(vols=0, sections=0, pairs=0, chao=0, ji=0,
                 anchors=len(anchors), tails=0, refined=0, ji_no_anchor=0)
    nav_vols = []
    for vi, vol in enumerate(HB):
        body, toc = [], []
        secno = 0
        cur_ch = None
        sid = 0
        emitted = set()

        def emit_ji(i):
            nonlocal sid
            z = ji[i]
            if not han(z['source']):
                return
            sid += 1
            u = dict(label='記文', source=z['source'], translation=z['translation'])
            body.append(emit_pair(u, '記', sid))
            stats['ji'] += 1
            stats['pairs'] += 1
            emitted.add(i)

        def emit_chao(ui):
            nonlocal sid
            u = chao[ui]
            sid += 1
            body.append(emit_pair(u, '鈔', sid))
            stats['chao'] += 1
            stats['pairs'] += 1

        units = [ui for ui, u in enumerate(chao) if u['vol'] == vol]
        # 卷首：先處理 chapter 0 的鈔；其餘按篇
        for ui in units:
            u = chao[ui]
            ch = u['chapter']
            if ch != cur_ch:
                if cur_ch == 0:
                    # 卷首尾巴（自序/序題/序文）已在下面處理
                    pass
                cur_ch = ch
                secno += 1
                if ch == 0:
                    title = '卷首'
                else:
                    title = '第%d篇　%s' % (ch, titles[ch][1])
                    if chap_vols[ch][0] != vol:
                        title += '（續）'
                toc.append([secno, title])
                body.append('<h2 class="sec" id="p%d">%s</h2>' % (secno, esc(title)))
                # 卷首專用：純記 + 鈔序對插
                if ch == 0:
                    # 先出前兩筆卷首資料（撰述、底本）
                    front = [x for x in units if chao[x]['chapter'] == 0]
                    for x in front[:2]:
                        emit_chao(x)
                        for i in by_anchor.get(x, []):
                            emit_ji(i)
                    # 元照自序／標五例：純記文
                    for i in by_anchor.get(-1, []):
                        emit_ji(i)
                    # 其餘鈔序逐段對插
                    rest = front[2:]
                    for x in rest:
                        emit_chao(x)
                        for i in by_anchor.get(x, []):
                            emit_ji(i)
                    continue
            if ch == 0:
                continue
            # 篇前記（錨在篇首之前）
            if ui == [x for x in units if chao[x]['chapter'] == ch][0]:
                for i in by_anchor.get(-1 - ui, []):  # 不用
                    emit_ji(i)
            emit_chao(ui)
            for i in by_anchor.get(ui, []):
                emit_ji(i)
        # 篇末尾巴（錨在最後一筆鈔之後）
        if units:
            last = units[-1]
            for i in by_anchor.get(last + 100000, []):
                emit_ji(i)
        if not body:
            raise SystemExit('%s 沒有內容' % vol)
        # 未輸出的記（錨在別卷／超出）：只在本卷有對應時補在卷末
        left = [i for i, z in enumerate(ji) if i not in emitted and i not in anchored
                and z['ch'] in chap_vols and chap_vols[z['ch']][0] == vol]
        for i in left:
            emit_ji(i)
            stats['ji_no_anchor'] += 1
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
            raise SystemExit('出現 <br><br>')
        io.open(os.path.join(OUT, vol + '.html'), 'w', encoding='utf-8').write(out)
        stats['vols'] += 1
        stats['sections'] += len(toc)
        nav_vols.append(dict(v=vol, secs=[['p%d' % n, t] for n, t in toc]))
        print(vol, '篇', len(toc), 'pair', sid, flush=True)

    import build_search_index as BSI
    BSI.build(site=SITE, only=['hebian'], quiet=True)

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

    print(json.dumps(stats, ensure_ascii=False))
    return stats


if __name__ == '__main__':
    main()
