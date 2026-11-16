# -*- coding: utf-8 -*-
"""產生「疏＋記」校閱材料（前後背景段數可調）。

用法：
  # 業疏指定的幾組，前後各 4 段
  python -X utf8 _src/mk_review_materials.py --book 業疏 --depth 4 \
         --out 測試/業疏_4段 --groups 6,11,14

  # 業疏全部可配對的組（每組一檔）
  python -X utf8 _src/mk_review_materials.py --book 業疏 --depth 4 --out 測試/業疏_全

  # 戒疏
  python -X utf8 _src/mk_review_materials.py --book 戒疏 --depth 4 --out 測試/戒疏_4段 --limit 20

說明：
  業疏 → TXT_分卷_標點/03_業疏_標註（已分【疏】【記】【序】）
  戒疏 → TXT_分卷/02_戒疏（自帶【律】【註】【疏】【記】）
  配對：一段連續【疏】＋其後連續【記】為一組。
"""
import argparse
import io
import json
import os

import materials_io as MI
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff]')

BOOKS = {
    '業疏': dict(src='TXT_分卷_標點/03_業疏_標註', tr='AI語譯/out/03_業疏', skip=0,
               shu='疏', ji='記', min_shu=40, max_shu=500, min_ji=40, max_ji=500),
    '戒疏': dict(src='TXT_分卷/02_戒疏', tr='AI語譯/out/02_戒疏', skip=5,
               shu='疏', ji='記', min_shu=40, max_shu=500, min_ji=40, max_ji=500),
    # 以下皆無記文，逐段為一組
    '尼鈔': dict(src='TXT_分卷/04_比丘尼鈔', tr='AI語譯/out/04_比丘尼鈔', skip=5,
               shu=None, ji=None, min_shu=1, max_shu=500),
    '行事鈔': dict(src='TXT_分卷/01_行事鈔', tr='AI語譯/out/01_行事鈔', skip=5,
                shu=None, ji=None, min_shu=1, max_shu=500),
    '義鈔': dict(src='TXT_分卷/05_拾毗尼義鈔_標點對齊', tr='AI語譯/out/05_拾毗尼義鈔', skip=5,
               shu=None, ji=None, min_shu=1, max_shu=500),
    '資持記': dict(src='TXT_分卷/資持記_細分', tr='AI語譯/out/資持記', skip=5,
                shu=None, ji=None, min_shu=1, max_shu=500, unit='記文'),
}

BASE_PROMPT = '你是南山律典審校編輯，負責校訂【{scope}】。\n\n### 原則\n1. 先依【原文】與律脈獨立拆解文法與主客關係，再核對【現譯】，勿順著譯文流暢度讀過；無誤之句照原譯保留，勿為修辭改動。\n2. 只改實質錯誤：主客施受、開遮模態、範圍與否定、斷句（含句尾虛字辨結上／領下）與引文邊界、部別與科判、無據增補或實詞漏譯，以及文言直抄、歐化倒裝等硬性語病。\n3. 正文不加解說圓括號（原文實質夾注與讀音除外）；須補明之主賓與條件直接融入正句。`〔補字〕`／`〔疑作X〕` 得保留，空白占位括號不強留。\n4. {book_ctx}{shuji_check}\n\n### 輸出（{split_target}；同一欄標籤只在開頭寫一次）：\n{out_format}'


def get_prompt(is_nicao=False):
    if is_nicao:
        return BASE_PROMPT.format(
            scope='鈔文',
            split_target='【鈔文】',
            book_ctx='',
            shuji_check='',
            out_format='     【鈔文】……',
        )
    return BASE_PROMPT.format(
        scope='疏文與記文',
        split_target='【疏文】與【記文】',
        book_ctx='《業疏》所釋「文／注」指《隨機羯磨》文注，《戒疏》所釋指《含注戒本》文注，「律／本律」方指《四分律》；',
        shuji_check='**【疏】【記】須雙向互核**：【記文】釋義須與【疏文】相契（不誤導、亦不隱沒所牒實詞），亦須以【疏文】前提檢核【記文】科判動詞。',
        out_format='     【疏文】……\n     【記文】……',
    )


def prompt_for(unit, book=''):
    """依實際單元標籤與書別產生提示詞（單邊段不再寫死鈔文）。"""
    from book_config import CFG
    cfg = CFG.get(book or '', {})
    ctx = (cfg.get('ctx') or ('', ''))[0] if unit in ('疏文', '記文', '律文', '註文', '序文') else ''
    chk = ''
    if unit == '鈔文' and cfg.get('note'):
        chk = cfg['note']
    if unit == '記文':
        chk = ('**【記文】須與所釋【疏文】／【鈔文】前提相契**：不誤導、亦不隱沒所牒實詞。'
               + ('；' + cfg.get('note', '') if cfg.get('note') else ''))
    return BASE_PROMPT.format(
        scope=unit, split_target='【%s】' % unit, extra_ban='',
        cite_source='', book_ctx=ctx, shuji_check=chk, tag_note='',
        out_format='     【%s】……' % unit, cite_ji='')


PROMPT = get_prompt(False)


def load_pair(spec, chunk):
    src = os.path.join(B, spec['src'].replace('/', os.sep), chunk + '.txt')
    tr = os.path.join(B, spec['tr'].replace('/', os.sep), chunk + '.txt')
    if not (os.path.exists(src) and os.path.exists(tr)):
        return None
    a = [x.strip() for x in
         io.open(src, encoding='utf-8', errors='ignore').read().split('\n')[spec.get('skip', 0):]
         if x.strip()]
    o = [x.strip() for x in re.split(r'(?:\r?\n){2,}',
                                     io.open(tr, encoding='utf-8', errors='ignore').read()) if x.strip()]
    if len(a) != len(o):
        print('  ⚠ 段落數不合，略過：%s（原文 %d／譯文 %d）' % (chunk, len(a), len(o)))
        return None
    labels = []
    for x in a:
        m = re.match(r'【(.)】', x)
        labels.append(m.group(1) if m else '?')
    return a, o, labels


def build_groups(spec):
    d = os.path.join(B, spec['src'].replace('/', os.sep))
    groups = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.txt'):
            continue
        chunk = fn[:-4]
        got = load_pair(spec, chunk)
        if not got:
            continue
        a, o, lab = got
        if spec.get('shu') is None:          # 無記文（如尼鈔）：逐段為一組
            n = len(a)
            k = 0
            while k < n:
                L = len(a[k])
                if spec.get('pack', True) and L < 100:
                    j, acc = k, 0
                    while (j < n and len(a[j]) < 100 and acc < 220 and (j - k) < 4):
                        acc += len(a[j])
                        j += 1
                    if j - k >= 2:
                        groups.append(dict(chunk=chunk, s0=k, s1=j, g0=j, g1=j,
                                           sl=acc, gl=0, a=a, o=o, no_ji=True,
                                           unit=spec.get('unit'), packed=True))
                        k = j
                        continue
                    # 孤立短段：併入後段，或併回前一組
                    if L <= ORPHAN_CHARS:
                        if k + 1 < n and len(a[k + 1]) <= 420:
                            groups.append(dict(chunk=chunk, s0=k, s1=k + 2, g0=k + 2,
                                               g1=k + 2, sl=L + len(a[k + 1]), gl=0,
                                               a=a, o=o, no_ji=True,
                                               unit=spec.get('unit'), packed=True))
                            k += 2
                            continue
                        if (groups and groups[-1]['chunk'] == chunk
                                and groups[-1]['s1'] == k and len(a[k - 1]) <= 420):
                            g = groups[-1]
                            g['s1'] = k + 1
                            g['g0'] = g['s1']
                            g['g1'] = g['s1']
                            g['sl'] += L
                            g['packed'] = True
                            k += 1
                            continue
                if spec['min_shu'] <= L <= spec['max_shu']:
                    groups.append(dict(chunk=chunk, s0=k, s1=k + 1, g0=k + 1, g1=k + 1,
                                       sl=L, gl=0, a=a, o=o, no_ji=True,
                                       unit=spec.get('unit')))
                k += 1
            continue
        i = 0
        covered = set()
        while i < len(a):
            if lab[i] != spec['shu']:
                i += 1
                continue
            s0 = i
            while i < len(a) and lab[i] == spec['shu']:
                i += 1
            s1 = i
            if s1 >= len(a) or lab[s1] != spec['ji']:
                continue
            g0 = s1
            while i < len(a) and lab[i] == spec['ji']:
                i += 1
            g1 = i
            sl = sum(len(a[k]) for k in range(s0, s1))
            gl = sum(len(a[k]) for k in range(g0, g1))
            if sl <= 0 or gl <= 0 or sl > spec['max_shu'] or gl > spec['max_ji']:
                continue
            groups.append(dict(chunk=chunk, s0=s0, s1=s1, g0=g0, g1=g1,
                               sl=sl, gl=gl, a=a, o=o))
            covered.update(range(s0, g1))

        # 未配對段（單邊疏／記、律文／註文／序文）另建單欄組，避免漏段
        unit_map = {'疏': '疏文', '記': '記文', '鈔': '鈔文',
                    '律': '律文', '註': '註文', '序': '序文'}
        i = 0
        while i < len(a):
            if i in covered:
                i += 1
                continue
            L = len(a[i])
            lb = unit_map.get(lab[i])
            if lb is None and L > 5:
                lb = ('疏文' if spec.get('shu') else '鈔文')
            if not (lb and L <= spec['max_shu'] and L >= 1):
                i += 1
                continue
            if L < 120:                      # 連續短段打包
                j, acc = i, 0
                while (j < len(a) and j not in covered
                       and unit_map.get(lab[j]) == lb
                       and len(a[j]) < 120 and acc < 460 and (j - i) < 10):
                    acc += len(a[j])
                    j += 1
                if j - i >= 2:
                    groups.append(dict(chunk=chunk, s0=i, s1=j, g0=j, g1=j,
                                       sl=acc, gl=0, a=a, o=o, no_ji=True,
                                       unit=lb, packed=True))
                    i = j
                    continue
            groups.append(dict(chunk=chunk, s0=i, s1=i + 1, g0=i + 1, g1=i + 1,
                               sl=L, gl=0, a=a, o=o, no_ji=True, unit=lb))
            i += 1
    return groups


ORPHAN_CHARS = 30
MAX_PRE_CHARS = 900
MAX_POST_CHARS = 600


def _cap(lines, max_chars):
    out, acc = [], 0
    for ln in lines:
        if acc + len(ln) > max_chars and out:
            break
        out.append(ln)
        acc += len(ln)
    return out or lines[:1]


def emit(g, front, back, outdir, idx, book=None):
    a, o = g['a'], g['o']
    s0, s1, g0, g1 = g['s0'], g['s1'], g['g0'], g['g1']

    def ctx(lo, hi):
        seg = [a[k] for k in range(lo, hi)]          # 保留【疏】【記】標籤
        return seg if seg else ['（本卷開頭）' if lo == 0 else '（本卷末尾）']

    pre = list(reversed(_cap(list(reversed(ctx(max(0, s0 - front), s0))),
                             MAX_PRE_CHARS)))
    post = _cap(ctx(g1, min(len(a), g1 + back)), MAX_POST_CHARS)
    unit = g.get('unit') or ('鈔文' if g.get('no_ji') else '疏文')
    body_prompt = (get_prompt(False) if (unit == '疏文' and g1 > g0)
                   else prompt_for(unit, book or ''))
    L = [body_prompt, '', '---', '',
         '（出處：《%s》%s，第 %d–%d 段）' % (book or '未知', g['chunk'], s0 + 1, g1), '',
         '【前文背景（僅供參考，嚴禁譯入正文）】', ''] + pre + ['']
    L += ['【本次待審單元】', '', '■ %s（原文）' % unit, '']
    _packed = bool(g.get('packed')) and (s1 - s0) > 1
    for n, k in enumerate(range(s0, s1), 1):
        _txt = re.sub(r'^【.】', '', a[k])
        L += [('[%d] ' % n if _packed else '') + _txt, '']
    if _packed:
        L += ['【分段要求】標籤只需寫在最開頭一次；其後逐條換行以 `[1] …`、`[2] …` 對應，'
              '勿在每個編號後重複標籤，亦勿合併、增減或改動編號；正文內部子條目序數一律用一、二、（一）（二），嚴禁額外使用 `[數字]`。', '']
    L += ['■ %s（現譯）' % unit, '']
    for n, k in enumerate(range(s0, s1), 1):
        _txt = re.sub(r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', o[k])
        L += [('[%d] ' % n if _packed else '') + _txt, '']
    if g1 > g0:                      # 有記文才輸出記文區塊
        L += ['■ 記文（原文）', '']
        for k in range(g0, g1):
            L += [re.sub(r'^【.】', '', a[k]), '']
        L += ['■ 記文（現譯）', '']
        for k in range(g0, g1):
            L += [re.sub(r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', o[k]), '']
    L += ['【後文背景（僅供參考，嚴禁譯入正文）】', ''] + post + ['']
    key = '%s_%04d' % (g['chunk'], s0 + 1)
    p = os.path.join(outdir, key + '.md')
    io.open(p, 'w', encoding='utf-8').write('\n'.join(L))
    def _mk(seq, start, end, strip_re):
        rows = []
        for n, k in enumerate(range(start, end), 1):
            txt = re.sub(strip_re, '', seq[k])
            rows.append((('[%d] ' % n) if _packed else '') + txt)
        return chr(10).join(rows)

    units = [{'lab': unit,
              'orig': _mk(a, s0, s1, r'^【.】'),
              'tr': _mk(o, s0, s1, r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*')}]
    if g1 > g0:
        units.append({'lab': '記文',
                      'orig': chr(10).join(re.sub(r'^【.】', '', a[k]) for k in range(g0, g1)),
                      'tr': chr(10).join(re.sub(r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', o[k])
                                         for k in range(g0, g1))})
    MI.write_json(outdir, key, {
        'key': key,
        'chunk': g['chunk'], 's0': s0, 's1': s1, 'g0': g0, 'g1': g1,
        'ex': '%s，第 %d–%d 段' % (g['chunk'], s0 + 1, g1),
        'pre': chr(10).join(pre),
        'post': chr(10).join(post),
        'book': book or '',
        'packed': bool(g.get('packed')),
        'segments': [re.sub(r'^【.】', '', a[k]) for k in range(s0, s1)]
                    if g.get('packed') else [],
        'units': units,
    })
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', default='業疏', choices=list(BOOKS))
    ap.add_argument('--depth', type=int, default=0, help='同時指定前後段數（0＝用 front/back）')
    ap.add_argument('--front', type=int, default=6)
    ap.add_argument('--back', type=int, default=4)
    ap.add_argument('--out', required=True)
    ap.add_argument('--groups', default='')
    ap.add_argument('--from-index', default='',
                    help='沿用既有 索引.json 的組別（欄位 no/chunk/s0）')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--shuffle-seed', type=int, default=0)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    if args.depth:
        args.front = args.back = args.depth
    spec = BOOKS[args.book]
    groups = build_groups(spec)
    print('%s：可配對 %d 組' % (args.book, len(groups)))
    if args.from_index:
        meta_old = json.load(io.open(os.path.join(B, args.from_index.replace('/', os.sep)),
                                     encoding='utf-8'))
        want = set()
        order = {}
        for m in meta_old:
            if isinstance(m, dict):                 # 本腳本輸出
                key = (m['chunk'], m['s0'])
                no = m['no']
            else:                                   # 舊格式 [no, chunk, start, end]
                no, chunk, st = m[0], m[1], m[2]
                key = (chunk, st)
            want.add(key)
            order[key] = no
        picked = [g for g in groups if (g['chunk'], g['s0'] + 1) in want]
        picked.sort(key=lambda g: order.get((g['chunk'], g['s0'] + 1), 999))
        groups = picked
        print('依 %s 取回 %d 組' % (args.from_index, len(groups)))
    elif args.groups:
        want = [int(x) for x in args.groups.split(',') if x.strip()]
        groups = [groups[i - 1] for i in want if 0 < i <= len(groups)]
    elif args.shuffle_seed:
        import random
        random.seed(args.shuffle_seed)
        random.shuffle(groups)
    if args.limit:
        groups = groups[:args.limit]

    outdir = os.path.join(B, args.out.replace('/', os.sep))
    if os.path.isdir(os.path.join(outdir, '回覆')) and os.listdir(os.path.join(outdir, '回覆')) and not args.force:
        raise SystemExit('輸出目錄已有回覆，請先移走或加 --force')
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.endswith(('.md', '.json')) and not f.startswith('索引'):
            os.remove(os.path.join(outdir, f))
    meta = []
    for i, g in enumerate(groups, 1):
        emit(g, args.front, args.back, outdir, i, args.book)
        meta.append({'no': i, 'chunk': g['chunk'], 's0': g['s0'] + 1, 'g1': g['g1'],
                     'shu_len': g['sl'], 'ji_len': g['gl']})
    json.dump(meta, io.open(os.path.join(outdir, '索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('已輸出 %d 份 → %s（前 %d 段、後 %d 段）' % (len(meta), args.out, args.front, args.back))
    for m in meta[:5]:
        print('  %02d %s 第 %d–%d 段｜疏%d字 記%d字' %
              (m['no'], m['chunk'], m['s0'], m['g1'], m['shu_len'], m['ji_len']))


if __name__ == '__main__':
    main()
