# -*- coding: utf-8 -*-
"""修訂後驗收閉環（verify_reaudit）：VERIFY 回覆 → 候選／重跑／人工清單。

流程（reaudit.txt 第 3/3 篇 §二、reaudit2.txt 去過擬合版）：
  1. 只處理 Step 2 判 FIX、且 Step 3 已產修訂回覆的單位。
  2. **只驗有實際改動的段**：修訂後與修訂前漢字完全相同者視為「正當維持原譯」
     （REVISE 合法駁回），直接列候選，不送 VERIFY、不重審合理未改項。
  3. 有改動者送 VERIFY（建議 QWEN_EFFORT=high、NO_WEB=1、MAX_LOCAL=2）：
       - 回覆 OK      → 寫候選 `回覆/<key>_回.txt`（可直接給 apply_reaudit --revise 使用）
       - 回覆 RETRY   → 把【未過原因】併入硬傷清單，產第二次 REVISE 材料（只重跑 1 次）
       - 二次仍 RETRY → `_人工複核清單.txt`（不再自動修）
  4. 幅度異常（新譯／原譯 >1.25 或 <0.70）強制進 VERIFY；缺回覆者列待跑。

本程式不呼叫 qwen、不改 `定稿/`、不寫 `定稿_v2`；只寫 `--out` 下的候選與清單。

用法：
  python -X utf8 _src/verify_reaudit.py --book 義鈔 --dry-run
  python -X utf8 _src/verify_reaudit.py --book 義鈔
  python -X utf8 _src/verify_reaudit.py --book 義鈔 --revise 重作材料_長段/_再審修訂/義鈔 \\
      --verify 重作材料_長段/_再驗/義鈔 --out 重作材料_長段/_驗收/義鈔
"""
import argparse
import datetime
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import book_config as BC          # noqa: E402
import materials_io as MI         # noqa: E402
import norm as NR                 # noqa: E402
import apply_reaudit as AR        # noqa: E402  只借回覆解析

MAX_RATIO = 1.25
MIN_RATIO = 0.70
_VERIFY_EFFORT = BC.STAGE_ENV.get('VERIFY', {}).get('QWEN_EFFORT', 'high')


def _resolve(p):
    p = str(p or '').replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


def _rel(p):
    try:
        return os.path.relpath(p, B)
    except ValueError:
        return p


def _han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s or ''))


def _read(p):
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else ''


def _unit_parts(meta):
    parts = []
    for p in (meta.get('parts') or []):
        parts.append({'lab': p.get('lab') or '鈔文',
                      'orig': p.get('orig') or '',
                      'tr': p.get('tr') or ''})
    return parts


def _norm_candidate(rt, parts, book=''):
    """把修訂回覆正規化；雙欄分欄各自對位原文。"""
    txt = (rt or '').strip()
    if not txt:
        return ''
    labs = [p['lab'] for p in parts if p['lab']]
    if len(set(labs)) > 1:
        by = {}
        for p in parts:
            by.setdefault(p['lab'], []).append(p['orig'])
        return NR.normalize_labeled(txt, by, ''.join(p['orig'] for p in parts)).strip()
    return NR.normalize(txt, ''.join(p['orig'] for p in parts)).strip()


def _changed_parts(before, after):
    """回傳有實際改動的段別（漢字比較）；空 list＝完全未改。"""
    if len(before) != len(after):
        return ['（段數不符）']
    changed = []
    for a, b in zip(before, after):
        if _han(a.get('tr')) != _han(b.get('tr')):
            changed.append(b.get('lab') or '?')
    return changed


def _ratio(before, after):
    ob = len(_han(''.join(p.get('tr') or '' for p in before)))
    nb = len(_han(''.join(p.get('tr') or '' for p in after)))
    return (float(nb) / ob) if ob else 0.0


_SECTION_STOPS = ('【前文背景', '【原文】', '【目前譯文】', '【前後鄰既有譯文',
                  '【跨段統一基準', '【必改硬傷】', '### 硬傷清單', '【硬傷清單',
                  '【初審檢索摘錄', '【後文背景', '【所釋鈔文', '【上一次驗收未過原因',
                  '【分段要求】')


def _sec_bounds(text, name):
    """取【name】區塊（止於下一個已知區塊標題，不把段別標籤當區塊界）。"""
    m = re.search(r'(?m)^\s*【%s】\s*$' % re.escape(name), text or '')
    if not m:
        return None
    tail = text[m.end():]
    end = len(text)
    for stop in _SECTION_STOPS:
        k = tail.find('\n' + stop)
        if k >= 0:
            end = min(end, m.end() + k)
    return (m.start(), end)


def _replace_sec(text, name, body):
    b = _sec_bounds(text, name)
    if b:
        return text[:b[0]] + '【%s】\n\n%s\n\n' % (name, body.strip()) + text[b[1]:]
    return text.rstrip() + '\n\n【%s】\n\n%s\n' % (name, body.strip())


def _replace_fixes(text, fixes):
    """換掉材料內的硬傷清單（相容【必改硬傷】與 ### 硬傷清單：兩種格式）。"""
    if '【必改硬傷】' in text:
        return _replace_sec(text, '必改硬傷', fixes)
    m = re.search(r'(?m)^(#{1,6}\s*)?硬傷清單[：:]\s*$', text or '')
    if not m:
        return text.rstrip() + '\n\n### 硬傷清單：\n\n' + fixes.strip() + '\n'
    nxt = re.search(r'(?m)^#{1,6}\s', text[m.end():])
    end = m.end() + nxt.start() if nxt else len(text)
    head = text[:m.start()]
    body = text[end:]
    return head + '### 硬傷清單：\n\n' + fixes.strip() + '\n\n' + body.lstrip()


def _build_retry_material(orig_md, candidate, merged_fixes, reasons, book='', key='',
                          parts=None):
    """以原修訂材料為底，換上新版提示詞、目前譯文與併合後的硬傷清單。"""
    txt = orig_md or ''
    _labs = [p['lab'] for p in (parts or []) if p.get('lab')]
    _src = '\n'.join((p.get('orig') or '') for p in (parts or []))
    _fmt = '\n'.join('【%s】……' % l for l in (list(dict.fromkeys(_labs)) or ['鈔文']))
    _prompt = BC.revise_prompt(book or None, None, _labs, _src, candidate,
                               key=key, fixes=merged_fixes, out_format=_fmt)
    if txt.strip() and '\n---\n' in txt:
        # 保留材料層（原文／目前譯文／摘錄），只換掉最前面的提示詞
        _rest = txt.split('\n---\n', 1)[1]
        txt = _prompt.rstrip() + '\n\n---\n' + _rest
    elif not txt.strip():
        txt = _prompt
    else:
        txt = _prompt.rstrip() + '\n\n---\n\n' + txt
    if '【目前譯文】' in txt:
        b = _sec_bounds(txt, '目前譯文')
        if b:
            txt = txt[:b[0]] + '【目前譯文】\n\n' + candidate.strip() + '\n\n' + txt[b[1]:]
    else:
        txt = txt.rstrip() + '\n\n【目前譯文】\n\n' + candidate.strip() + '\n'
    txt = _replace_fixes(txt, merged_fixes)
    return txt


def _merge_fixes(old_fixes, reasons):
    out = (old_fixes or '').strip()
    if reasons:
        out += '\n\n（上一次 VERIFY 未過原因，須一併改妥）\n' + reasons.strip()
    return out.strip()


def _context_from_material(md):
    """從修訂材料抽出【前文背景】【對照層】【後文背景】，供 VERIFY 參閱。"""
    if not md:
        return ''
    out = []
    for prefix in ('前文背景', '對照層', '後文背景'):
        m = re.search(r'(?m)^【%s[^】]*】\s*$' % prefix, md)
        if not m:
            continue
        tail = md[m.end():]
        nxt = re.search(r'(?m)^【[^】\n]{1,30}】\s*$', tail)
        body = tail[:nxt.start()] if nxt else tail
        head = md[m.start():m.end()].strip()
        if body.strip():
            out.append(head + '\n\n' + body.strip())
    return '\n\n'.join(out)


def _verify_material(book, key, parts, fixes, before_text, after_text, vol='',
                     context=''):
    """產出 VERIFY 材料：原文＋前後文／對照層＋硬傷清單＋修訂前後譯文。"""
    src = '\n'.join('■ %s（原文）\n\n%s\n' % (p['lab'], p['orig'].strip())
                    for p in parts if (p.get('orig') or '').strip())
    L = [BC.verify_prompt(book, BC.note_for(book, [p['lab'] for p in parts])), '',
         '---', '', '（出處：《%s》%s，%s）' % (book, vol or '（未分卷）', key), '']
    if context:
        L += ['【前後文與對照層（僅供核對，嚴禁抄入譯文）】', '', context, '']
    L += ['【原文】', '', src, '',
          '【硬傷清單】', '', (fixes or '（無）').strip(), '',
          '【修訂前譯文】', '', before_text.strip(), '',
          '【修訂後譯文】', '', after_text.strip(), '']
    return '\n'.join(L)


def _write(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    io.open(path, 'w', encoding='utf-8').write(text)


def main():
    ap = argparse.ArgumentParser(
        description='VERIFY 回退閉環：OK 寫候選、RETRY 併硬傷重跑一次、二次 RETRY 進人工清單'
                    '（不呼叫 qwen、不改定稿）')
    ap.add_argument('--book', default='', choices=[''] + list(BC.BOOKS),
                    help='書別（決定預設目錄）')
    ap.add_argument('--revise', default='', help='修訂材料目錄（預設 測試/重譯/<book>/_再審修訂）')
    ap.add_argument('--verify', default='', help='驗收材料目錄（預設 測試/重譯/<book>/_再驗）')
    ap.add_argument('--out', default='', help='輸出目錄（預設 重作材料_長段/_驗收/<book>）')
    ap.add_argument('--reason-from', default='',
                    help='幅度／待驗收清單（預設 <out>/_待驗收清單.txt 或 <revise>/_待驗收清單.txt）')
    ap.add_argument('--no-materials', action='store_true', help='不產 VERIFY／再修材料，只做分流')
    ap.add_argument('--dry-run', action='store_true', help='只統計，不寫任何檔案')
    args = ap.parse_args()

    if not args.book and not (args.revise and args.verify):
        raise SystemExit('需要 --book，或同時給 --revise 與 --verify')
    book = args.book
    revise = _resolve(args.revise or ('測試/重譯/%s/_再審修訂' % book))
    verify = _resolve(args.verify or ('測試/重譯/%s/_再驗' % book))
    out = _resolve(args.out or ('重作材料_長段/_驗收/%s' % book))
    if not os.path.isdir(revise):
        raise SystemExit('找不到修訂材料目錄：' + revise)

    idx = {}
    ip = os.path.join(revise, '索引.json')
    if os.path.exists(ip):
        try:
            idx = json.load(io.open(ip, encoding='utf-8'))
        except Exception:
            idx = {}
    keys = list(idx.get('FIX') or [])
    if not keys:
        rep = os.path.join(revise, '回覆')
        if os.path.isdir(rep):
            keys = sorted(f[:-7] for f in os.listdir(rep) if f.endswith('_回.txt'))
    if not keys:
        print('修訂目錄內沒有 FIX 單位（索引.json／回覆/ 皆空）：%s' % _rel(revise))
        return

    # 幅度／人工標記來源
    reasons_file = (_resolve(args.reason_from) if args.reason_from else '')
    if not reasons_file:
        for _cand in (os.path.join(out, '_待驗收清單.txt'),
                      os.path.join(revise, '_待驗收清單.txt')):
            if os.path.exists(_cand):
                reasons_file = _cand
                break
    forced = set()
    if reasons_file and os.path.exists(reasons_file):
        for ln in io.open(reasons_file, encoding='utf-8'):
            _k = ln.split('\t')[0].strip()
            if _k:
                forced.add(_k)

    rep_rev = os.path.join(revise, '回覆')
    rep_ver = os.path.join(verify, '回覆')
    buckets = {'candidate': [], 'unchanged': [], 'retry_material': [],
               'verify_pending': [], 'second_pending': [], 'manual': [],
               'pending_revise': [], 'abnormal': []}
    notes = {}

    for key in keys:
        meta = {}
        mp = os.path.join(revise, key + '.json')
        if os.path.exists(mp):
            try:
                meta = json.load(io.open(mp, encoding='utf-8'))
            except Exception:
                meta = {}
        parts = _unit_parts(meta)
        fixes = meta.get('fixes') or ''
        vol = meta.get('vol') or ''
        _book = book or (meta.get('book') or '')
        if _book not in BC.BOOKS:
            _book = BC.book_of(revise)
        rt1 = _read(os.path.join(rep_rev, key + '_回.txt'))
        if not rt1.strip():
            buckets['pending_revise'].append(key)
            continue
        new_parts, why = AR._parse_reply(rt1, parts)
        if new_parts is None:
            buckets['abnormal'].append('%s：%s' % (key, why))
            continue
        cand1 = _norm_candidate(rt1, parts, book)
        after1 = [{'lab': p['lab'], 'tr': t} for p, t in zip(parts, new_parts)]
        changed = _changed_parts(parts, after1)
        ratio = _ratio(parts, after1)

        if not changed and key not in forced:
            # 正當駁回／完全未改：不送 VERIFY，直接列候選
            buckets['unchanged'].append(key)
            notes[key] = '未改動（REVISE 正當維持原譯；不重審）'
            if not args.dry_run:
                _write(os.path.join(out, '回覆', key + '_回.txt'), cand1)
            continue

        v1 = _read(os.path.join(rep_ver, key + '_回.txt'))
        if not v1.strip():
            buckets['verify_pending'].append(
                '%s\t%s' % (key, '幅度 %.2f 須驗收' % ratio if
                            (ratio > MAX_RATIO or ratio < MIN_RATIO) else '有改動待 VERIFY'))
            if not args.no_materials and not args.dry_run:
                _ctx = _context_from_material(_read(os.path.join(revise, key + '.md')))
                _write(os.path.join(verify, key + '.md'),
                       _verify_material(_book, key, parts, fixes,
                                        '\n'.join('【%s】\n%s' % (p['lab'], p['tr'])
                                                  for p in parts), cand1, vol,
                                        context=_ctx))
            continue
        vd = MI.verify_verdict(v1)
        if vd == 'OK':
            buckets['candidate'].append(key)
            notes[key] = 'VERIFY OK'
            if not args.dry_run:
                _write(os.path.join(out, '回覆', key + '_回.txt'), cand1)
            continue
        if vd == 'ERROR':
            buckets['abnormal'].append('%s：VERIFY 回覆無法判定' % key)
            continue
        # RETRY（第一次）
        reasons = MI.verify_reasons(v1) or '（未寫原因，請重審上一次改動句）'
        merged = _merge_fixes(fixes, reasons)
        rt2 = _read(os.path.join(rep_rev, key + '_再修_回.txt'))
        if not rt2.strip():
            buckets['retry_material'].append('%s\t%s' % (key, reasons.split('\n')[0][:120]))
            if not args.no_materials and not args.dry_run:
                _write(os.path.join(out, '_再修', key + '.md'),
                       _build_retry_material(_read(os.path.join(revise, key + '.md')),
                                             cand1, merged, reasons,
                                             book=_book, key=key, parts=parts))
            continue
        # 已有第二次修訂：需第二次 VERIFY
        new2, why2 = AR._parse_reply(rt2, parts)
        if new2 is None:
            buckets['abnormal'].append('%s：二次修訂回覆 %s' % (key, why2))
            continue
        cand2 = _norm_candidate(rt2, parts, book)
        v2 = _read(os.path.join(rep_ver, key + '_再驗_回.txt'))
        if not v2.strip():
            buckets['second_pending'].append(key)
            if not args.no_materials and not args.dry_run:
                _ctx = _context_from_material(_read(os.path.join(revise, key + '.md')))
                _write(os.path.join(verify, key + '_再驗.md'),
                       _verify_material(_book, key, parts, merged, cand1, cand2, vol,
                                        context=_ctx))
            continue
        vd2 = MI.verify_verdict(v2)
        if vd2 == 'OK':
            buckets['candidate'].append(key)
            notes[key] = '二次 VERIFY OK'
            if not args.dry_run:
                _write(os.path.join(out, '回覆', key + '_回.txt'), cand2)
        else:
            buckets['manual'].append(
                '%s\t二次 VERIFY 仍 %s：%s'
                % (key, vd2 if vd2 != 'ERROR' else '無法判定',
                   (MI.verify_reasons(v2) or '（未寫原因）').split('\n')[0][:160]))

    print('驗收分流（%s）：FIX %d 單位' % (book or '（未指定書）', len(keys)))
    print('  候選 %d（其中未改動 %d）、待 VERIFY %d、待二次修訂 %d、待二次驗收 %d、'
          '人工 %d、缺修訂 %d、異常 %d'
          % (len(buckets['candidate']) + len(buckets['unchanged']),
             len(buckets['unchanged']), len(buckets['verify_pending']),
             len(buckets['retry_material']), len(buckets['second_pending']),
             len(buckets['manual']), len(buckets['pending_revise']),
             len(buckets['abnormal'])))
    for label, lst in (('待 VERIFY', buckets['verify_pending']),
                       ('待二次修訂', buckets['retry_material']),
                       ('待二次驗收', buckets['second_pending']),
                       ('人工複核', buckets['manual']),
                       ('異常', buckets['abnormal'])):
        if lst:
            print('  %s：%s' % (label, '；'.join(lst[:5])))

    if args.dry_run:
        print('  （--dry-run：未寫任何檔案；VERIFY effort 建議 %s）' % _VERIFY_EFFORT)
        return

    os.makedirs(out, exist_ok=True)
    _write(os.path.join(out, '_人工複核清單.txt'),
           ''.join(x + '\n' for x in buckets['manual']))
    _write(os.path.join(out, '_待重跑清單.txt'),
           ''.join(x + '\n' for x in (buckets['verify_pending']
                                      + buckets['retry_material']
                                      + buckets['second_pending'])))
    _write(os.path.join(out, '_缺修訂清單.txt'),
           ''.join(x + '\n' for x in buckets['pending_revise']))
    _write(os.path.join(out, '_異常清單.txt'),
           ''.join(x + '\n' for x in buckets['abnormal']))
    _write(os.path.join(out, '_驗收說明.md'),
           '\n'.join([
               '# 驗收閉環說明（%s）' % (book or '未指定書'), '',
               '- VERIFY effort 建議：`%s`（不用 medium，避免弱否決強）' % _VERIFY_EFFORT,
               '- 只驗有實際改動的段；未改動者視為 REVISE 正當維持原譯，直接列候選。',
               '- 候選位置：`回覆/<key>_回.txt`，可直接給 '
               '`apply_reaudit.py --revise <本目錄>` 使用。',
               '- `_再修/<key>.md` 為第一次 RETRY 後的第二次修訂材料（只重跑一次）。',
               '- 第二次仍 RETRY 者列 `_人工複核清單.txt`，不再自動修。', '']))
    manifest = {'generated': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'book': book, 'revise': _rel(revise), 'verify': _rel(verify),
                'out': _rel(out), 'verify_effort': _VERIFY_EFFORT,
                'total_fix': len(keys), 'buckets': buckets, 'notes': notes,
                'forced_verify': sorted(forced)}
    io.open(os.path.join(out, '_驗收狀態.json'), 'w', encoding='utf-8').write(
        json.dumps(manifest, ensure_ascii=False, indent=1))
    print('  候選 → %s' % _rel(os.path.join(out, '回覆')))
    print('  狀態 → %s' % _rel(os.path.join(out, '_驗收狀態.json')))


if __name__ == '__main__':
    main()
