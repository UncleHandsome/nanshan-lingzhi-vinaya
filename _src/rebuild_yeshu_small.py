# -*- coding: utf-8 -*-
"""業疏：只用小單位重建定稿，頁面 pair 補缺口。

2026-11-21 lead 修正：docs/yeshu 是舊譯，不可用來補缺口；main 已不再呼叫
load_page_pairs／fill_gaps，新來源沒有的段落保留為缺口。

來源：
  測試/重譯/業疏/_終審/*.md
  測試/重譯/業疏/_終審_已有定稿_排除/*.md（14 個已有 _定稿 的單位）
  測試/重譯/業疏/_終修_20261121/回覆/<key>_回.txt
  測試/重譯/業疏/_定稿/<key>.txt
  原文：TXT/03_四分律刪補隨機羯磨疏.txt

輸出：定稿/yeshu.jsonl（只含新譯單位；缺口不補）
"""
import argparse
import collections
import difflib
import glob
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '業疏')
TXT = os.path.join(B, 'TXT', '03_四分律刪補隨機羯磨疏.txt')
OUT = os.path.join(B, '定稿', 'yeshu.jsonl')
BAK = os.path.join(B, '定稿', '_舊_yeshu.jsonl')
REPORT = os.path.join(B, '重作材料_長段', '業疏_重建結果.md')

SEC_RE = re.compile(r'(?m)^【(原文|待審譯文|裁決[^】]*|後文背景[^】]*|前文背景[^】]*|結論|必改硬傷)】\s*$')
BLOCK_RE = re.compile(r'■\s*([^\n（]{0,12})（原文）')
TAG_RE = re.compile(r'【\s*(疏文|記文|记文|鈔文|钞文|律文|註文|注文|序文|疏|記|记|鈔|钞|律|註|注|序)\s*】')

TAGMAP = {
    '疏文': '疏文', '疏': '疏文',
    '記文': '記文', '记文': '記文', '記': '記文', '记': '記文',
    '鈔文': '鈔文', '钞文': '鈔文', '鈔': '鈔文', '钞': '鈔文',
    '律文': '律文', '律': '律文',
    '註文': '註文', '注文': '註文', '註': '註文', '注': '註文',
    '序文': '序文', '序': '序文',
}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def sections(md):
    return [(m.start(), m.end(), m.group(1)) for m in SEC_RE.finditer(md)]


def get_section(md, prefix):
    ms = [m for m in sections(md) if m[2].startswith(prefix)]
    return ms[-1] if ms else None


def section_region(md, prefix):
    sec = get_section(md, prefix)
    if not sec:
        return ''
    start, end, _ = sec
    for s, e, name in sections(md):
        if s >= end and not name.startswith(prefix):
            return md[end:s]
    return md[end:]


def parse_blocks(md):
    reg = section_region(md, '原文')
    if not reg:
        return []
    out = []
    ms = list(BLOCK_RE.finditer(reg))
    for i, m in enumerate(ms):
        a = m.end()
        b = ms[i + 1].start() if i + 1 < len(ms) else len(reg)
        src = reg[a:b].strip()
        src = re.sub(r'\n\s*---\s*$', '', src).strip()
        out.append((m.group(1).strip(), src))
    return out


def split_translation(text, nblocks):
    text = (text or '').strip()
    if not text:
        return []
    ms = list(TAG_RE.finditer(text))
    parts = []
    if not ms:
        parts = [(None, text)]
    else:
        pre = text[:ms[0].start()].strip()
        if pre:
            parts.append((None, pre))
        for i, m in enumerate(ms):
            a = m.end()
            b = ms[i + 1].start() if i + 1 < len(ms) else len(text)
            parts.append((TAGMAP[m.group(1)], text[a:b].strip()))
    if len(parts) == nblocks:
        return parts
    if len(parts) == 1 and nblocks > 1:
        chunks = [x.strip() for x in re.split(r'\n\s*\n', parts[0][1]) if x.strip()]
        if len(chunks) == nblocks:
            return [(None, x) for x in chunks]
    return parts


def para_split(text):
    text = (text or '').strip()
    chunks = [x.strip() for x in re.split(r'\n\s*\n', text) if x.strip()]
    if len(chunks) == 1 and '\n' in text:
        chunks = [x.strip() for x in text.split('\n') if x.strip()]
    return chunks


def load_units():
    units = {}
    for p in sorted(glob.glob(os.path.join(ROOT, '_終審', '*.md'))):
        key = os.path.basename(p)[:-3]
        md = io.open(p, encoding='utf-8').read()
        blocks = parse_blocks(md)
        if not blocks:
            continue
        parts = split_translation(section_region(md, '待審譯文'), len(blocks))
        units[key] = {'segments': [{'label': l, 'source': s} for l, s in blocks],
                      'trans': parts, 'revised': False, 'origin': '終審'}
    for p in sorted(glob.glob(os.path.join(ROOT, '_終審_已有定稿_排除', '*.md'))):
        key = os.path.basename(p)[:-3]
        md = io.open(p, encoding='utf-8').read()
        blocks = parse_blocks(md)
        if not blocks:
            continue
        fin = os.path.join(ROOT, '_定稿', key + '.txt')
        tr = io.open(fin, encoding='utf-8').read() if os.path.exists(fin) else section_region(md, '待審譯文')
        parts = split_translation(tr, len(blocks))
        units[key] = {'segments': [{'label': l, 'source': s} for l, s in blocks],
                      'trans': parts, 'revised': True, 'origin': '定稿'}
    for p in sorted(glob.glob(os.path.join(ROOT, '_終修_20261121', '回覆', '*_回.txt'))):
        key = os.path.basename(p)[:-6]
        if key not in units:
            continue
        tr = io.open(p, encoding='utf-8').read()
        units[key]['trans'] = split_translation(tr, len(units[key]['segments']))
        units[key]['revised'] = True
        units[key]['origin'] = 'FIX'
    return units


def clean_tr(tr):
    tr = (tr or '').strip()
    tr = re.split(r'\n\s*【(?:分段要求|必改硬傷|逐句簡核|結論|待審|裁決|後文背景)', tr)[0].strip()
    tr = re.sub(r'\n\s*---\s*$', '', tr).strip()
    tr = re.sub(r'\s*（出處：[^）]*）\s*$', '', tr).strip()
    return tr


def trans_text(unit, i):
    parts = unit.get('trans') or []
    if i < len(parts):
        return parts[i][1]
    return ''


def apply_special_repairs(units):
    """修復 _終審 打包錯置的 5 個區塊（0042/0046/0047、02a_0001/0004）。"""
    repaired = []

    # --- 01a 0042 / 0046 ---
    k42 = '01a_卷一之一_0042'
    k46 = '01a_卷一之一_0046'
    if k42 in units and k46 in units:
        u42 = units[k42]
        sp = para_split(u42['segments'][1]['source'])
        tp = para_split(trans_text(u42, 1))
        if len(sp) == 2 and len(tp) == 2:
            u46 = units[k46]
            src46 = re.sub(r'^\s*(?:【)?\s*疏\s*】\s*', '', u46['segments'][0]['source'])
            units[k42] = {
                'segments': [u42['segments'][0], {'label': '記文', 'source': sp[1]}],
                'trans': [u42['trans'][0], ('記文', tp[1])],
                'revised': u42['revised'], 'origin': u42['origin'] + '_修',
            }
            units[k46] = {
                'segments': [{'label': '疏文', 'source': src46}, {'label': '記文', 'source': sp[0]}],
                'trans': [u46['trans'][0], ('記文', tp[0])],
                'revised': u46['revised'], 'origin': u46['origin'] + '_修',
            }
            repaired.append((k42, '記文拆兩段，後段歸 0046'))
            repaired.append((k46, '疏文去「疏】」污染，補記文（0042 前段）'))

    # --- 02a 0001 / 0004 -> 0001 / 0002 / 0004 ---
    k1 = '02a_卷一之二_0001'
    k4 = '02a_卷一之二_0004'
    k2 = '02a_卷一之二_0002'
    if k1 in units and k4 in units and len(units[k1]['segments']) == 2 and len(units[k4]['segments']) == 2:
        u1 = units[k1]
        u4 = units[k4]
        sp1 = para_split(u1['segments'][1]['source'])
        tp1 = para_split(trans_text(u1, 1))
        sp4 = para_split(u4['segments'][0]['source'])
        tp4 = para_split(trans_text(u4, 0))
        if len(sp1) == 2 and len(tp1) == 2 and len(sp4) == 2 and len(tp4) == 2:
            units[k1] = {
                'segments': [u1['segments'][0], {'label': '記文', 'source': sp1[1]}],
                'trans': [u1['trans'][0], ('記文', tp1[1])],
                'revised': u1['revised'], 'origin': u1['origin'] + '_修',
            }
            units[k2] = {
                'segments': [{'label': '疏文', 'source': sp4[1]}, {'label': '記文', 'source': sp1[0]}],
                'trans': [('疏文', tp4[1]), ('記文', tp1[0])],
                'revised': False, 'origin': '終審_拆分',
            }
            units[k4] = {
                'segments': [{'label': '疏文', 'source': sp4[0]}, u4['segments'][1]],
                'trans': [('疏文', tp4[0]), u4['trans'][1]],
                'revised': u4['revised'], 'origin': u4['origin'] + '_修',
            }
            repaired.append((k1, '記文拆兩段，前段歸新 0002'))
            repaired.append((k2, '新單位：0004 疏文後段 + 0001 記文前段'))
            repaired.append((k4, '疏文拆兩段，後段歸新 0002'))
    return repaired


class Locator:
    def __init__(self, h):
        self.h = h
        self.idx8 = collections.defaultdict(list)
        for i in range(len(h) - 7):
            self.idx8[h[i:i + 8]].append(i)

    def exact(self, s, expected):
        for n in (20, 16, 12, 10, 8, 6, 4):
            if len(s) >= n:
                q = self.h.find(s[:n])
                if q >= 0:
                    pos = []
                    while q >= 0:
                        pos.append(q)
                        q = self.h.find(s[:n], q + 1)
                    return min(pos, key=lambda x: (abs(x - expected), x))
        return None

    def fuzzy(self, s, expected):
        if len(s) < 8:
            return None
        votes = collections.defaultdict(float)
        span = len(s) - 7
        step = max(1, span // 30)
        for i in range(0, span, step):
            gram = s[i:i + 8]
            pos = self.idx8.get(gram)
            if not pos or len(pos) > 3000:
                continue
            w = 1.0 / (1.0 + len(pos) ** 0.5)
            for p in pos:
                st = p - i
                if 0 <= st <= len(self.h) - len(s):
                    votes[st] += w
        if not votes:
            return None
        cands = sorted(votes, key=lambda x: (-votes[x], abs(x - expected)))[:12]
        best = None
        best_score = -1
        for st in cands:
            ratio = difflib.SequenceMatcher(None, s, self.h[st:st + len(s)], autojunk=False).ratio()
            # 位置接近 expected 者略加分
            score = ratio + max(0.0, 0.1 - abs(st - expected) / max(1, len(self.h)))
            if score > best_score:
                best_score = score
                best = (st, ratio)
        return best

    def locate(self, s, expected):
        q = self.exact(s, expected)
        if q is not None:
            ratio = difflib.SequenceMatcher(None, s, self.h[q:q + len(s)], autojunk=False).ratio()
            return q, ratio, 'exact'
        got = self.fuzzy(s, expected)
        if got:
            return got[0], got[1], 'fuzzy'
        return None


def build_rows(units, loc):
    h = loc.h
    rows = []
    cur = 0
    issues = []
    positions = {}
    for key in sorted(units):
        u = units[key]
        segs = []
        starts = []
        for bi, seg in enumerate(u['segments']):
            s = han(seg['source'])
            if not s:
                issues.append((key, bi, 'EMPTY', 0.0))
                continue
            got = loc.locate(s, cur + 20)
            if not got:
                issues.append((key, bi, 'NOLOC', 0.0))
                continue
            q, ratio, method = got
            if ratio < 0.8:
                issues.append((key, bi, 'LOW', ratio, q))
            starts.append((q, q + len(s)))
            segs.append((seg, q, ratio, method))
            cur = max(cur, q + len(s))
        if not segs:
            continue
        # 特別：0047 記文用鄰居缺口定位
        if key == '01a_卷一之一_0047' and len(segs) == 2 and segs[1][2] < 0.85:
            prev_end = segs[0][1] + len(han(segs[0][0]['source']))
            k46 = '01a_卷一之一_0046'
            # 0002 的疏文起點即 0046 疏文起點
            if k46 in units:
                s46 = han(units[k46]['segments'][0]['source'])
                q46 = h.find(s46[:20], prev_end)
                if q46 > prev_end:
                    segs[1] = (segs[1][0], prev_end, 0.0, 'neighbor')
                    starts[-1] = (prev_end, q46)
        a = min(x[0] for x in starts)
        b = max(x[1] for x in starts)
        positions[key] = (a, b)
        seg_out = []
        tr_out = []
        for i, (seg, q, ratio, method) in enumerate(segs):
            tr = clean_tr(trans_text(u, i))
            tr = re.sub(r'^\s*【[^】]{1,6}】\s*', '', tr).strip()
            seg_out.append({'label': seg['label'], 'source': seg['source'], 'translation': tr})
            tr_out.append('【%s】%s' % (seg['label'], tr))
        rows.append({
            'book': '業疏', 'book_id': 'yeshu', 'key': key,
            'label': seg_out[0]['label'],
            'source': '\n\n\n\n'.join(x['source'] for x in seg_out),
            'translation': '\n'.join(tr_out),
            'revised': bool(u['revised']),
            'segments': seg_out,
            'raw_start': a, 'raw_end': b,
            'vol': '', 'chunk': '',
            '_origin': u['origin'],
        })
    return rows, issues, positions


def dedupe(rows):
    seen = set()
    out = []
    removed = 0
    for r in sorted(rows, key=lambda x: (x['raw_start'], x['raw_end'], x['key'])):
        k = (r['raw_start'], r['raw_end'], r['source'])
        if k in seen:
            removed += 1
            continue
        seen.add(k)
        out.append(r)
    return out, removed


def resolve_overlaps(rows):
    rows = sorted(rows, key=lambda x: (x['raw_start'], -x['raw_end']))
    kept = []
    fixed = []
    for r in rows:
        if kept and r['raw_start'] < kept[-1]['raw_end']:
            p = kept[-1]
            ov = p['raw_end'] - r['raw_start']
            if r['raw_end'] <= p['raw_end']:
                # 被前段包住；同原文才丟
                if r['source'] == p['source']:
                    fixed.append((r['key'], p['key'], ov, 'drop-contained'))
                    continue
                r['raw_start'] = p['raw_end']
                if r['raw_start'] >= r['raw_end']:
                    continue
                fixed.append((r['key'], p['key'], ov, 'trim-start'))
            else:
                p['raw_end'] = r['raw_start']
                fixed.append((r['key'], p['key'], ov, 'trim-prev-end'))
        kept.append(r)
    return kept, fixed


def snap_small_gaps(rows, h, maxlen=12):
    """把 2–12 字的邊界缺口依「原文比 source 長」的一側併入相鄰單位。"""
    gaps, _ = compute_gaps(rows, len(h))
    snapped = []
    for a, b in gaps:
        if b - a > maxlen:
            continue
        prev = [r for r in rows if r['raw_end'] <= a]
        nxt = [r for r in rows if r['raw_start'] >= b]
        if not prev or not nxt:
            continue
        p = prev[-1]
        n = nxt[0]
        pd = (p['raw_end'] - p['raw_start']) - len(han(p['source']))
        nd = (n['raw_end'] - n['raw_start']) - len(han(n['source']))
        if pd >= nd:
            p['raw_end'] = b
            snapped.append((a, b, p['key'], 'prev'))
        else:
            n['raw_start'] = a
            snapped.append((a, b, n['key'], 'next'))
    return snapped


def compute_gaps(rows, n):
    cov = [0] * n
    for r in rows:
        for i in range(max(0, r['raw_start']), min(n, r['raw_end'])):
            cov[i] += 1
    gaps = []
    i = 0
    while i < n:
        if cov[i] == 0:
            j = i
            while j < n and cov[j] == 0:
                j += 1
            gaps.append((i, j))
            i = j
        else:
            i += 1
    overlap = sum(1 for c in cov if c > 1)
    return gaps, overlap


def assign_vol_chunk(rows):
    # 依位置找最近的非 GAP 單位的 chunk
    anchors = sorted([r for r in rows if not r['key'].startswith('GAP')], key=lambda x: x['raw_start'])
    for r in rows:
        if r['key'].startswith('GAP') or not r['chunk']:
            is_vol_title = r['source'].lstrip().startswith('四分律刪補隨機羯磨疏濟緣記卷')
            best = None
            for a in anchors:
                if a['raw_start'] <= r['raw_start']:
                    best = a
                else:
                    if best is None or is_vol_title:
                        best = a
                    break
            if best:
                r['chunk'] = best['chunk']
                r['vol'] = best['vol']
    for r in rows:
        if not r['chunk']:
            r['chunk'] = '00_卷首'
            r['vol'] = '卷一'
        if not r['vol']:
            r['vol'] = r['chunk'].split('_')[1][:2] if '_' in r['chunk'] else '卷一'


def set_chunk(rows):
    for r in rows:
        key = r['key']
        if key.startswith('GAP'):
            continue
        parts = key.split('_')
        if len(parts) >= 2:
            r['chunk'] = parts[0] + '_' + parts[1]
            tail = parts[1]
            m = re.match(r'(卷[一二三四])', tail)
            r['vol'] = m.group(1) if m else '卷一'
        else:
            r['chunk'] = '00_卷首'
            r['vol'] = '卷一'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()

    raw = io.open(TXT, encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    print('raw han', len(h))

    units = load_units()
    print('units', len(units), 'blocks', sum(len(u['segments']) for u in units.values()))
    repaired = apply_special_repairs(units)
    print('repaired', repaired)
    print('units after repair', len(units), 'blocks', sum(len(u['segments']) for u in units.values()))

    loc = Locator(h)
    rows, issues, positions = build_rows(units, loc)
    print('rows', len(rows), 'issues', len(issues))
    for x in issues:
        print('  ISSUE', x)

    rows, removed = dedupe(rows)
    print('dedupe removed', removed)
    rows, fixed = resolve_overlaps(rows)
    print('overlap fixes', len(fixed))
    for x in fixed[:30]:
        print('  OV', x)

    set_chunk(rows)
    snapped = snap_small_gaps(rows, h)
    print('snapped tiny gaps', len(snapped))
    gaps, overlap = compute_gaps(rows, len(h))
    print('gaps', len(gaps), 'gap chars', sum(b - a for a, b in gaps), 'overlap', overlap)
    for g in gaps:
        if g[1] - g[0] >= 8:
            print('  GAP', g, g[1] - g[0], h[g[0]:g[0] + 28])

    if not args.write:
        return

    # 依 lead 2026-11-21 修正：不再用 docs/yeshu 舊頁補缺口。
    # 新來源（_終審／_終修_20261121/回覆／_定稿）沒有的段落，保留缺口。
    all_rows = rows
    set_chunk(all_rows)
    assign_vol_chunk(all_rows)
    all_rows = sorted(all_rows, key=lambda x: (x['raw_start'], x['raw_end']))

    # 移除內部欄位
    for r in all_rows:
        r.pop('_origin', None)

    if not os.path.exists(BAK):
        shutil.copy2(OUT, BAK)
        print('backup ->', BAK)
    with io.open(OUT, 'w', encoding='utf-8') as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    gaps2, overlap2 = compute_gaps(all_rows, len(h))
    print('FINAL rows', len(all_rows), 'gaps', len(gaps2), 'gapchars', sum(b - a for a, b in gaps2),
          'overlap', overlap2, 'unlocated', sum(1 for r in all_rows if r['raw_start'] < 0))
    for a, b in gaps2:
        print('  FINALGAP', a, b, b - a, h[a:a + 35])


if __name__ == '__main__':
    main()
