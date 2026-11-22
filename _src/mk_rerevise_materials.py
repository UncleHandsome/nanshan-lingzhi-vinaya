# -*- coding: utf-8 -*-
"""只為 FIX 單位產生「單段修訂」材料（第二階段再審後的定點修訂）。

材料內容：
  - 【原文】：該單位的全部段別（parts；疏＋記不拆）
  - 【目前譯文】：該單位現譯（逐段標籤，供修訂後同位輸出）
  - 前後原文（前 ≤1500 字、後 ≤600 字）與前後鄰既有譯文（前 ≤400、後 ≤300）
  - 【跨段統一基準】：鄰段共用譯詞對照＋硬傷所涉原詞在鄰段的譯法
  - 【必改硬傷】：來自 _再審拆回_計畫.json 的該單位項目
  - 【初審檢索摘錄】：由該再審包的 <pack>_evid.json 依硬傷過濾（mk_revise_materials.evidence_block）

用法：
  python -X utf8 _src/mk_rerevise_materials.py \
      --materials 重作材料_長段/_再審材料/業疏 \
      --out 重作材料_長段/_再審修訂/業疏

輸出：
  <out>/<unit_key>.md／.json、<out>/索引.json；修訂回覆放 <out>/回覆/<unit_key>_回.txt。
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import book_config as BC  # noqa: E402
import mk_reaudit_materials as RA  # noqa: E402  只用常數與 clip 工具

PLAN_NAME = '_再審拆回_計畫.json'
PRE_SRC_CAP = 1800
PRE_TR_CAP = 400
POST_SRC_CAP = 600
POST_TR_CAP = 300
TERM_CAP = 12
FIX_TERM_CAP = 6

RA_REVISE_PROMPT = BC.REVISE_PROMPT


def _resolve(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


def _rel(p):
    try:
        return os.path.relpath(p, B)
    except ValueError:
        return p


def _h12(s):
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()[:12]


def _unit_tr(u):
    return '\n'.join(p.get('tr', '') for p in (u.get('parts') or []))


def _unit_orig(u):
    return '\n'.join(p.get('orig', '') for p in (u.get('parts') or []))


def _frag(text, term, radius=14):
    i = (text or '').find(term)
    if i < 0:
        return '—'
    a = max(0, i - radius)
    b = min(len(text), i + len(term) + radius)
    return text[a:b].replace('\n', ' ')


STOP_CHARS = set(
    '的了著是在把被將與及或而則以於之其此彼所為無有不得應須當如若使皆並又即乃但故'
    '也矣焉哉乎者我汝今昔上下前後中內外一二三四五六七八九十百千萬箇些更最亦皆')


def _cands(text):
    out = {}
    for run in re.findall(r'[\u4e00-\u9fff]{2,}', text or ''):
        for n in (2, 3, 4):
            for i in range(0, len(run) - n + 1):
                g = run[i:i + n]
                if all(c in STOP_CHARS for c in g):
                    continue
                out[g] = out.get(g, 0) + 1
    return out


def _term_table(unit, prev_u, next_u, cap=TERM_CAP):
    """本單位現譯與前／後鄰現譯共用、且多見於原文的專詞（2–4 字）。"""
    tr = _unit_tr(unit)
    prev = _unit_tr(prev_u) if prev_u else ''
    nxt = _unit_tr(next_u) if next_u else ''
    if not (prev or nxt):
        return []
    orig = RA.han(_unit_orig(unit) + (_unit_orig(prev_u) if prev_u else '')
                  + (_unit_orig(next_u) if next_u else ''))
    c_unit = _cands(tr)
    c_prev = _cands(prev)
    c_next = _cands(nxt)
    forced = set()
    for g in re.findall(r'《([^》]{2,20})》', tr):
        if g in prev or g in nxt:
            forced.add(g)
    for g in re.findall(r'[「『]([^」』]{2,10})[」』]', tr):
        if len(g) <= 8 and (g in prev or g in nxt):
            forced.add(g)
    blocked = []
    for _s in (tr, prev, nxt):
        blocked += re.findall(r'《([^》]{2,30})》', _s)
        blocked += re.findall(r'[「『]([^」』]{2,30})[」』]', _s)
    scored = {}
    for g, c in c_unit.items():
        in_prev = g in c_prev
        in_next = g in c_next
        in_orig = g in orig
        both = in_prev and in_next
        if not (in_prev or in_next):
            continue
        if not (in_orig or both or c >= 2):
            continue
        if any(g in b and g != b for b in blocked):
            continue
        sc = (3 if in_orig else 0) + (2 if both else 1) + min(c, 3) \
            + (3 if g in forced else 0) + 0.5 * len(g)
        scored[g] = sc
    keys = sorted(scored, key=lambda g: (-scored[g], -len(g), g))
    keep = []
    for g in keys:
        if any(g != k and g in k for k in keep):
            continue
        keep.append(g)
        if len(keep) >= cap:
            break
    for g in sorted(forced, key=lambda s: -len(s)):
        if g in keep or any(g in k for k in keep) or any(k in g for k in keep):
            continue
        keep.append(g)
        if len(keep) >= cap:
            break
    return [(g, _frag(prev, g) if prev else '—',
             _frag(nxt, g) if nxt else '—') for g in keep]


def _fix_terms(fixes, prev_u, next_u, cap=FIX_TERM_CAP):
    """硬傷清單中「原文『X』」的 X，在鄰段現譯的用法（多為保留原詞）。"""
    terms = []
    for t in re.findall(r'原文[「『]([^」』]{1,40})[」』]', fixes or ''):
        t = t.strip()
        if t and t not in terms:
            terms.append(t)
    prev = _unit_tr(prev_u) if prev_u else ''
    nxt = _unit_tr(next_u) if next_u else ''
    return [(t, _frag(prev, t) if prev else '—',
             _frag(nxt, t) if nxt else '—') for t in terms[:cap]]


def _neighbors(pack, no):
    us = pack.get('units') or []
    prev_u = us[no - 2] if no - 2 >= 0 else None
    next_u = us[no] if no < len(us) else None
    # 單段包：用 pack 的前後鄰背景當 pseudo unit，讓詞表／硬傷原詞仍有前後鄰
    if prev_u is None and (pack.get('pre_tr') or pack.get('pre_src')):
        prev_u = {'parts': [{'orig': pack.get('pre_src', ''),
                             'tr': pack.get('pre_tr', '')}]}
    if next_u is None and (pack.get('post_tr') or pack.get('post_src')):
        next_u = {'parts': [{'orig': pack.get('post_src', ''),
                             'tr': pack.get('post_tr', '')}]}
    return prev_u, next_u


def _contexts(pack, no):
    us = pack.get('units') or []
    prev_u, next_u = _neighbors(pack, no)
    if no > 1:
        # 中間單位：往前回溯多個短單位，湊滿 PRE_SRC_CAP（不可只看前一個）
        acc, total = [], 0
        for u in reversed(us[:no - 1]):
            s = _unit_orig(u)
            acc.insert(0, s)
            total += len(s)
            if total >= PRE_SRC_CAP:
                break
        pre_src = RA._clip_tail('\n'.join(acc), PRE_SRC_CAP)
        pre_tr = RA._clip_tail(_unit_tr(prev_u), PRE_TR_CAP) if prev_u else ''
    else:
        pre_src, pre_tr = pack.get('pre_src', ''), pack.get('pre_tr', '')
    if next_u:
        post_src = RA._clip_head(_unit_orig(next_u), POST_SRC_CAP)
        post_tr = RA._clip_head(_unit_tr(next_u), POST_TR_CAP)
    else:
        post_src, post_tr = pack.get('post_src', ''), pack.get('post_tr', '')
    return {'pre_src': pre_src, 'pre_tr': pre_tr,
            'post_src': post_src, 'post_tr': post_tr,
            'prev_key': (prev_u or {}).get('key', pack.get('prev_unit', '')),
            'next_key': (next_u or {}).get('key', pack.get('next_unit', ''))}


def _out_format(labs):
    labs = list(labs) or ['鈔文']   # 同標籤多段不可去重，否則第 2 段遺失
    return '\n'.join('【%s】……' % lab for lab in labs)


_REF_STOPS = ('前文背景', '後文背景', '原文', '目前譯文', '前後鄰既有譯文',
              '跨段統一基準', '本次待審單元', '必改硬傷', '硬傷清單')


def _ref_block(path):
    """從單段再審材料抽出【對照層】，止於下一個白名單 section（段別標籤不算）。"""
    if not os.path.exists(path):
        return ''
    t = io.open(path, encoding='utf-8').read()
    m = re.search(r'(?m)^【對照層[^】]*】\s*$', t)
    if not m:
        return ''
    tail = t[m.end():]
    nxt = re.search(r'(?m)^【(?:%s)[^】]*】\s*$'
                    % '|'.join(re.escape(x) for x in _REF_STOPS), tail)
    return (tail[:nxt.start()] if nxt else tail).strip()


def _render(prompt, book, vol, key, pack_key, no, contexts, unit, fixes,
            terms, fix_terms, evid, refs='', mother=''):
    L = [prompt, '', '---', '',
         '（出處：《%s》%s，%s｜再審包 %s 第 %d 號）'
         % (book, vol or '（未分卷）', key, pack_key, no), '']
    if contexts['pre_src'].strip():
        L += ['【前文背景（原文，僅供銜接，嚴禁譯入正文）】', '',
              contexts['pre_src'], '']
    if (mother or '').strip():
        L += ['【所釋鈔文（資持記母本；僅供對讀，嚴禁抄入譯文）】', '',
              mother.strip(), '']
    if (refs or '').strip():
        L += ['【對照層（僅供校勘，嚴禁譯入正文）】', '', refs.strip(), '']
    L += ['【原文】', '']
    for p in unit.get('parts') or []:
        L += ['■ %s（原文）' % p.get('lab', ''), '']
        if p.get('dirty_orig'):
            L += ['〔定稿殘留：此段含 %s；逐字照錄〕' % '／'.join(p['dirty_orig']), '']
        L += [(p.get('orig') or '').strip(), '']
    L += ['【目前譯文】', '']
    for p in unit.get('parts') or []:
        L += ['【%s】' % p.get('lab', '')]
        if p.get('dirty_tr'):
            L += ['〔定稿殘留：此段含 %s；逐字照錄〕' % '／'.join(p['dirty_tr'])]
        L += [(p.get('tr') or '').strip(), '']
    if contexts.get('pre_tr', '').strip() or contexts.get('post_tr', '').strip():
        L += ['【前後鄰既有譯文（僅供對齊用詞，嚴禁照抄整句）】', '']
        if contexts.get('pre_tr', '').strip():
            L += ['■ 前鄰單位（%s）' % (contexts.get('prev_key') or '—'), '',
                  contexts['pre_tr'], '']
        if contexts.get('post_tr', '').strip():
            L += ['■ 後鄰單位（%s）' % (contexts.get('next_key') or '—'), '',
                  contexts['post_tr'], '']
    L += ['【跨段統一基準（僅供對齊用詞，嚴禁照抄整句）】', '']
    L += ['- 段別：%s；%s' % ('、'.join('【%s】' % x for x in unit.get('labs') or []),
                            BC.note_for(book, unit.get('labs')))]
    L += ['- 體例底線：%s' % BC.CITE_STYLE_MIN]
    if contexts['prev_key'] or contexts['next_key']:
        L += ['- 前鄰單位：%s；後鄰單位：%s'
              % (contexts['prev_key'] or '（無）', contexts['next_key'] or '（無）')]
    if terms:
        L += ['', '| 共用譯詞 | 前鄰段現譯片段 | 後鄰段現譯片段 |',
              '|:--|:--|:--|']
        for t, a, b in terms:
            L.append('| %s | %s | %s |' % (t, a, b))
        L += ['', '（上列為本單位現譯與前／後鄰現譯共用的譯詞；修訂涉及其一者須全段一致，'
              '不得為對齊抄入鄰段整句。）']
    else:
        L += ['- 本單位與前後鄰段無明顯共用譯詞；仍須保持段別體例與專詞一致。']
    if fix_terms:
        L += ['', '| 硬傷所涉原詞 | 前鄰段現譯用法 | 後鄰段現譯用法 |',
              '|:--|:--|:--|']
        for t, a, b in fix_terms:
            L.append('| %s | %s | %s |' % (t, a, b))
    L += ['', '【必改硬傷】', '', fixes.strip(), '']
    if evid:
        L += ['【初審檢索摘錄（僅供核對依據，嚴禁抄入譯文）】', '', evid, '']
    if contexts['post_src'].strip():
        L += ['【後文背景（原文，僅供銜接，嚴禁譯入正文）】', '',
              contexts['post_src'], '']
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(
        description='只為再審 FIX 單位產生單段修訂材料（不呼叫 qwen）')
    ap.add_argument('--book', default='', help='書別（決定 --materials／--out 預設）')
    ap.add_argument('--materials', default='',
                    help='再審材料目錄（預設 測試/重譯/<book>/_再審）')
    ap.add_argument('--plan', default='', help='拆回計畫（預設 <materials>/%s）' % PLAN_NAME)
    ap.add_argument('--out', default='', help='修訂材料輸出目錄（預設 測試/重譯/<book>/_再審修訂）')
    ap.add_argument('--max-evidence', type=int, default=2200,
                    help='檢索摘錄字數上限（預設 2200）')
    ap.add_argument('--no-evidence', action='store_true', help='不附檢索摘錄')
    ap.add_argument('--force', action='store_true', help='允許覆寫既有材料')
    ap.add_argument('--dry-run', action='store_true', help='只統計，不寫檔')
    args = ap.parse_args()

    if not args.materials:
        if not args.book:
            raise SystemExit('需要 --materials 或 --book（例：--book 義鈔）')
        args.materials = '測試/重譯/%s/_再審' % args.book
    if not args.out:
        if not args.book:
            raise SystemExit('需要 --out（或加 --book 用預設目錄）')
        args.out = '測試/重譯/%s/_再審修訂' % args.book
    mdir = _resolve(args.materials)
    plan_path = (_resolve(args.plan) if args.plan
                 else os.path.join(mdir, PLAN_NAME))
    if not os.path.exists(plan_path):
        raise SystemExit('找不到拆回計畫：' + plan_path)
    plan = json.load(io.open(plan_path, encoding='utf-8'))
    fix = plan.get('fix') or {}
    out = _resolve(args.out)
    rep = os.path.join(mdir, '回覆')
    if not fix:
        print('計畫內沒有 FIX 單位；不產材料。')
        return
    if args.dry_run:
        print('FIX 單位 %d 個；--dry-run 不寫檔。' % len(fix))
        for k, v in list(fix.items())[:5]:
            print('  %s（%s 第 %d 號，%d 項）'
                  % (k, v.get('pack', ''), v.get('no', 0), len(v.get('items') or [])))
        return
    os.makedirs(out, exist_ok=True)
    _rep = os.path.join(out, '回覆')
    if os.path.isdir(_rep) and any(f.endswith('_回.txt') for f in os.listdir(_rep)) \
            and not args.force:
        raise SystemExit('（已中止）輸出目錄已有修訂回覆，重產材料會錯位：%s\n'
                         '  確定重跑請加 --force，或改用新目錄。' % out)
    for f in list(os.listdir(out)):
        if f.endswith(('.md', '.json')) and not f.startswith('索引'):
            try:
                os.remove(os.path.join(out, f))
            except OSError:
                pass

    packs = {}
    order = {}
    n = 0
    skipped = []
    for key, info in sorted(fix.items(),
                            key=lambda kv: (kv[1].get('pack', ''), kv[1].get('no', 0))):
        pack_key = info.get('pack') or ''
        no = int(info.get('no') or 0)
        if pack_key not in packs:
            p = os.path.join(mdir, pack_key + '.json')
            if not os.path.exists(p):
                skipped.append((key, '缺材料 %s' % pack_key))
                continue
            packs[pack_key] = json.load(io.open(p, encoding='utf-8'))
        pack = packs[pack_key]
        us = pack.get('units') or []
        if not (1 <= no <= len(us)) or us[no - 1].get('key') != key:
            skipped.append((key, '計畫編號與材料不符（%s 第 %d 號）' % (pack_key, no)))
            continue
        unit = us[no - 1]
        book = pack.get('book') or ''
        vol = unit.get('vol') or pack.get('vol') or ''
        fixes = '\n'.join(it.get('text', '') for it in (info.get('items') or []))
        if not fixes.strip():
            skipped.append((key, '無硬傷文字'))
            continue
        ctx = _contexts(pack, no)
        prev_u, next_u = _neighbors(pack, no)
        terms = _term_table(unit, prev_u, next_u)
        fix_terms = _fix_terms(fixes, prev_u, next_u)
        evid = ''
        if not args.no_evidence:
            try:
                from mk_revise_materials import evidence_block
                evid = evidence_block(rep, pack_key, fixes,
                                      max_chars=args.max_evidence)
            except Exception:
                evid = ''
        note = BC.note_for(book, unit.get('labs') or [])
        _src = '\n'.join((p.get('orig') or '') for p in unit.get('parts') or [])
        _tr = '\n'.join((p.get('tr') or '') for p in unit.get('parts') or [])
        prompt = BC.revise_prompt(
            book, note, unit.get('labs') or [], _src, _tr,
            long=bool(re.search(r'_L\d{3,}', key)),
            key=key, fixes=fixes,
            out_format=_out_format(unit.get('labs') or []))
        _mother = pack.get('mother') or ''
        if book == '資持記':
            try:
                import mother_corpus as MC
                _mother = MC.chao_for(_src) or _mother
            except Exception:
                pass
        md = _render(prompt, book, vol, key, pack_key, no, ctx, unit, fixes,
                     terms, fix_terms, evid,
                     refs=_ref_block(os.path.join(mdir, pack_key + '.md')),
                     mother=_mother)
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write(md)
        meta = {
            'key': key, 'pack': pack_key, 'book': book, 'chunk': unit.get('chunk', ''),
            'vol': vol, 'labs': unit.get('labs') or [],
            'fixes': fixes,
            'parts': [{'lab': p.get('lab'), 'orig': p.get('orig'), 'tr': p.get('tr'),
                       'dirty': list(p.get('dirty') or []),
                       'dirty_orig': list(p.get('dirty_orig') or []),
                       'dirty_tr': list(p.get('dirty_tr') or []),
                       'hash': p.get('hash')} for p in unit.get('parts') or []],
            'pre_src': ctx['pre_src'], 'pre_tr': ctx['pre_tr'],
            'post_src': ctx['post_src'], 'post_tr': ctx['post_tr'],
            'prev_unit': ctx['prev_key'], 'next_unit': ctx['next_key'],
            'evidence': bool(evid),
            'hash': unit.get('hash') or _h12(fixes),
            'chars': {'src': sum(len(RA.han(p.get('orig', '')))
                                 for p in unit.get('parts') or []),
                      'tr': sum(len(RA.han(p.get('tr', '')))
                                for p in unit.get('parts') or [])},
        }
        io.open(os.path.join(out, key + '.json'), 'w', encoding='utf-8').write(
            json.dumps(meta, ensure_ascii=False, indent=1))
        order[key] = n + 1
        n += 1
    json.dump({'plan': _rel(plan_path), 'book': plan.get('book', ''),
               'FIX': list(order), 'materials': n},
              io.open(os.path.join(out, '索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if skipped:
        print('  ⚠ 略過 %d 個 FIX 單位：' % len(skipped))
        for k, why in skipped[:10]:
            print('    %s：%s' % (k, why))
    print('已產生 %d 份單段修訂材料 → %s' % (n, _rel(out)))


if __name__ == '__main__':
    main()
