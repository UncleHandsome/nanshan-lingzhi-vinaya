# -*- coding: utf-8 -*-
"""再審回覆拆回：驗證【分段核驗表】涵蓋 [01]..[N]，異常改 _異常.txt，拆出 FIX 計畫。

規則（與 mk_reaudit_materials.py 的材料格式配套）：
  1. 每檔材料含 N 個單位（`### [01]（key: …）`）。
  2. 回覆必須有【分段核驗表】，且編號 [01]..[N] 一個不漏、不得越界。
  3. 缺表、漏號、越界、截斷、400 內容審查 → 回覆改名（或另存）`_異常.txt`，
     並記入 `_異常清單.log`；不計入 FIX／PASS。
  4. 【必改硬傷】逐項行首 [n] 對回單位；未被點名的單位一律 PASS。
  5. `--bisect`：對異常檔自動對半切成兩個小材料（<key>_b1／_b2）放進 _bisect/，
     供補跑；切半不呼叫 qwen。

用法：
  python -X utf8 _src/split_reaudit.py --materials 重作材料_長段/_再審材料/業疏
  python -X utf8 _src/split_reaudit.py --materials ... --bisect
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials_io as MI

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

PLAN_NAME = '_再審拆回_計畫.json'
_NUM_RE = re.compile(r'\[\s*(\d{1,3})\s*(?:[-–—~～至]\s*(\d{1,3})\s*)?\]')
_ITEM_RE = re.compile(
    r'^\s*(?:[-*•]|\d+[.、．])?\s*(?:\*\*|__|`)?\s*\[\s*(\d{1,3})\s*\]')
_CONT_RE = re.compile(r'^(?:\s{2,}|\t|(?:問題|依據|修正方向|→|說明)[：:])')
_SEC_RE = re.compile(r'(?m)^[ \t#*>\-]*【([^】\n]{1,24})】')


def _resolve(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


def _rel(p):
    try:
        return os.path.relpath(p, B)
    except ValueError:
        return p


_BLOCK_SECTIONS = ('分段核驗表', '必改硬傷', '可斟酌微瑕', '備註', '結論', '說明', '核驗說明', '核對紀要')


def _block(text, name):
    """取【name】區塊；只認明確 section 標題，段別【疏文】等不得當邊界。"""
    names = tuple(dict.fromkeys((name,) + _BLOCK_SECTIONS))
    rx = re.compile(r'(?m)^[ \t#*>\-]*【(%s)】'
                    % '|'.join(re.escape(x) for x in names))
    marks = [(m.start(), m.end(), m.group(1).strip())
             for m in rx.finditer(text or '')]
    # 相容 markdown 標題：### 分段核驗表／### 必改硬傷
    for m in re.finditer(r'(?m)^#{1,6}\s*(%s)\s*$'
                         % '|'.join(re.escape(x) for x in names), text or ''):
        marks.append((m.start(), m.end(), m.group(1).strip()))
    marks.sort()
    for i, (s, e, title) in enumerate(marks):
        if title == name or title.startswith(name):
            end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
            body = text[e:end].strip()
            body = re.split(r'(?m)^\s*(?:核驗說明|【結論】|【說明】)', body)[0].strip()
            return body
    i = (text or '').find('【%s】' % name)
    if i < 0:
        return None
    nxt = re.search(r'(?m)^[ \t#*>\-]*【(?:%s)】'
                    % '|'.join(re.escape(x) for x in names), text[i + len(name) + 2:])
    j = i + len(name) + 2 + nxt.start() if nxt else len(text)
    body = text[i + len(name) + 2:j].strip()
    return re.split(r'(?m)^\s*(?:核驗說明|【結論】|【說明】)', body)[0].strip()


def _nums(s):
    out = set()
    s = re.sub(r'\]\s*[-–—~～至]\s*\[', '-', s or '')
    for m in _NUM_RE.finditer(s):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a:
            a, b = b, a
        if b - a > 500:
            out.add(a)
            continue
        out.update(range(a, b + 1))
    return out


def _is_none(txt):
    s = re.sub(r'[\s*_`#>\-•]', '', txt or '')
    if s in ('', '無', '無。', '无', '无。', '沒有', '没有'):
        return True
    # 單段常見「無（只有…）」：無 [n] 問題欄位即視為無硬傷
    if s.startswith(('無', '无')) and not re.search(r'\[\d', s) \
            and not re.search(r'問題[:：]|修正方向[:：]', s):
        return True
    return MI.verdict('【必改硬傷】\n' + (txt or '')) == 'PASS'


def _parse_items(body, n_units):
    """回傳 (items, bad_numbers, unattributed)；bad_numbers 為越界或非數字段號。"""
    items, bad, loose = [], [], 0
    cur = None
    for raw in (body or '').splitlines():
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if re.match(r'^\s*(?:核驗說明|【結論】|【說明】)', ln):
            break
        m = _ITEM_RE.match(ln)
        if m:
            n = int(m.group(1))
            cur = {'n': n, 'text': ln.strip()}
            if 1 <= n <= n_units:
                items.append(cur)
            else:
                bad.append(n)
            continue
        if cur is not None and (ln.startswith(('  ', '\t')) or _CONT_RE.match(ln)
                                or not ln.lstrip().startswith('【')):
            cur['text'] += '\n' + ln.strip()
            continue
        cur = None
        if re.search(r'[須應補刪改修缺漏誤錯]', ln):
            loose += 1
    return items, bad, loose


def _unbalanced(t, src=''):
    """只判回覆比原文多出的不平衡；原文本身引號不全不當截斷。"""
    for a, b, label in (('「', '」', '「」'), ('『', '』', '『』'),
                        ('（', '）', '（）'), ('《', '》', '《》'),
                        ('〔', '〕', '〔〕')):
        d = (t or '').count(a) - (t or '').count(b)
        s = (src or '').count(a) - (src or '').count(b)
        if d and d != s and abs(d) > abs(s):
            return label + ' 未成對'
    return ''


def _classify(reply_path, meta, key):
    """回傳 (status, reason, reply_text, items)。status: ok／pending／abnormal。"""
    rep_dir = os.path.dirname(reply_path)
    p400 = os.path.join(rep_dir, key + '_400審查.txt')
    pcut = os.path.join(rep_dir, key + '_截斷.txt')
    pabn = os.path.join(rep_dir, key + '_異常.txt')
    n = len(meta.get('units') or [])
    if os.path.exists(p400):
        return 'abnormal', '內容審查未通過（400）', None, []
    if not os.path.exists(reply_path):
        if os.path.exists(pcut):
            return 'abnormal', '截斷（僅有 _截斷.txt）', None, []
        if os.path.exists(pabn):
            return 'abnormal', '先前異常，尚未重跑（見 _異常.txt）', None, []
        return 'pending', '', None, []
    try:
        rt = io.open(reply_path, encoding='utf-8').read()
    except Exception as e:
        return 'abnormal', '回覆無法讀取：%s' % e, None, []
    if len(re.sub(r'\s', '', rt)) < 8:
        return 'abnormal', '回覆空白', rt, []
    tbl = _block(rt, '分段核驗表')
    if tbl is None:
        # 單段容錯：無表但有【結論】PASS／FIX，或硬傷無 [01] 時歸 unit 1
        if n == 1 and MI.verdict(rt) == 'PASS':
            return 'ok', '', rt, []
        if n == 1 and MI.verdict(rt) == 'FIX':
            fx = _block(rt, '必改硬傷')
            if fx and not _is_none(fx):
                return 'ok', '', rt, [{'n': 1, 'text': fx.strip()}]
        return 'abnormal', '缺【分段核驗表】', rt, []
    covered = _nums(tbl)
    if not covered:
        return 'abnormal', '【分段核驗表】無編號', rt, []
    missing = [i for i in range(1, n + 1) if i not in covered]
    extra = sorted(x for x in covered if not 1 <= x <= n)
    if missing:
        return ('abnormal', '漏號：%s' % '、'.join('[%02d]' % i for i in missing[:20]),
                rt, [])
    if extra:
        return ('abnormal', '編號越界：%s' % '、'.join('[%d]' % i for i in extra[:20]),
                rt, [])
    fixes = _block(rt, '必改硬傷')
    if fixes is None:
        return 'abnormal', '缺【必改硬傷】', rt, []
    if _is_none(fixes):
        return 'ok', '', rt, []
    src_all = '\n'.join(p.get('orig') or ''
                        for u in (meta.get('units') or [])
                        for p in (u.get('parts') or []))
    items, bad, loose = _parse_items(fixes, n)
    if n == 1 and not bad and (not items or loose):
        # 單段：硬傷未標 [01] 時整段歸 unit 1，不整筆異常
        items, loose = [{'n': 1, 'text': fixes.strip()}], 0
    if bad:
        return ('abnormal',
                '硬傷段號越界：%s' % '、'.join('[%d]' % x for x in bad[:20]), rt, [])
    if loose:
        return ('abnormal',
                '【必改硬傷】有 %d 行未標單位號（須以 [n] 起頭）' % loose, rt, [])
    if not items:
        return 'abnormal', '【必改硬傷】有內容但無法拆回', rt, []
    return 'ok', '', rt, items


def _write_abnormal(reply_path, key, reason, reply_text, dry_run):
    abn = os.path.join(os.path.dirname(reply_path), key + '_異常.txt')
    if dry_run:
        return abn
    body = '# 異常：%s\n\n' % reason
    if reply_text:
        body += reply_text
    else:
        body += '（本檔無可解析回覆；請看 %s_400審查.txt／%s_截斷.txt 或材料重跑）\n' % (key, key)
    io.open(abn, 'w', encoding='utf-8').write(body)
    if os.path.exists(reply_path):
        try:
            os.remove(reply_path)
        except OSError:
            pass
    return abn


def _unit_from_json(d):
    """把材料 json 的 unit 還原成 mk_reaudit_materials 的 unit 結構（供切半）。"""
    parts = []
    for p in d.get('parts') or []:
        parts.append({'lab': p.get('lab', ''), 'orig': p.get('orig', ''),
                      'tr': p.get('tr', ''), 'start': p.get('start', -1),
                      'end': p.get('end', -1), 'raw_ok': p.get('raw_ok'),
                      'dirty': list(p.get('dirty') or []),
                      'dirty_orig': list(p.get('dirty_orig') or []),
                      'dirty_tr': list(p.get('dirty_tr') or [])})
    return {'key': d.get('key', ''), 'row': {}, 'chunk': d.get('chunk', ''),
            'vol': d.get('vol', ''), 'raw_start': d.get('raw_start', -1),
            'raw_end': d.get('raw_end', -1), 'labs': list(d.get('labs') or []),
            'parts': parts, 'hash': d.get('hash', ''),
            'src_hash': d.get('src_hash', ''),
            'raw_ok': d.get('raw_ok'), 'dirty': list(d.get('dirty') or []),
            'mono': True, 'parts_joined': d.get('parts_joined', True)}


def _bisect(meta, outdir, dry_run):
    """把一個異常 pack 對半切成兩份材料；回傳子 key 清單。"""
    import mk_reaudit_materials as RA
    units = [_unit_from_json(x) for x in (meta.get('units') or [])]
    n = len(units)
    if n < 2:
        return []
    mid = n // 2
    halves = [(units[:mid], '1/2'), (units[mid:], '2/2')]
    keys = []
    gaps_all = meta.get('gaps') or []
    for hi, (half, part) in enumerate(halves, 1):
        if not half:
            continue
        child = '%s_b%d' % (meta['key'], hi)
        if hi == 1:
            pre = (meta.get('pre_src', ''), meta.get('pre_tr', ''))
        else:
            pre = RA.context_before(units, mid)
        if hi == 2:
            post = (meta.get('post_src', ''), meta.get('post_tr', ''))
        else:
            post = RA.context_after(units, mid - 1)
        _ks = {u['key'] for u in half}
        gaps = [g for g in gaps_all
                if g.get('after') in _ks or g.get('before') in _ks]
        # 子包也要帶對照層（去重、≤2800），不可只有母包有
        refs, seen_ref, ref_len = [], set(), 0
        for j, u in enumerate(half):
            for title, body in RA.reference_blocks(meta.get('book', ''), u, half, j):
                sig = re.sub(r'\s+', '', body or '')[:80]
                if not sig or sig in seen_ref or ref_len + len(body) > 2800:
                    continue
                seen_ref.add(sig)
                refs.append((title, body))
                ref_len += len(body)
        if not dry_run:
            RA.emit_pack(outdir, half, 0, meta.get('book', ''),
                         meta.get('book_id', ''), meta.get('count_mode', 'both'),
                         gaps, None, pre=pre, post=post,
                         parent=meta['key'], part=part, key=child,
                         refs=refs)
        keys.append(child)
    return keys


def main():
    ap = argparse.ArgumentParser(
        description='驗證再審回覆的【分段核驗表】，異常改 _異常.txt，拆出 FIX／PASS 計畫')
    ap.add_argument('--materials', default='',
                    help='再審材料目錄（預設 測試/重譯/<book>/_再審）')
    ap.add_argument('--out', default='', help='計畫輸出目錄（預設同 --materials）')
    ap.add_argument('--plan-name', default=PLAN_NAME, help='計畫檔名（預設 %s）' % PLAN_NAME)
    ap.add_argument('--book', default='', help='書別（同時決定預設材料目錄；預設全部）')
    ap.add_argument('--bisect', action='store_true', help='異常檔自動對半切，產 _bisect/ 小材料')
    ap.add_argument('--bisect-out', default='', help='切半輸出目錄（預設 <materials>/_bisect）')
    ap.add_argument('--min-units', type=int, default=2, help='可切半的最少單位數（預設 2）')
    ap.add_argument('--dry-run', action='store_true', help='只檢查與統計，不改名、不寫檔')
    args = ap.parse_args()

    if not args.materials:
        if not args.book:
            raise SystemExit('需要 --materials 或 --book（例：--book 義鈔）')
        args.materials = '測試/重譯/%s/_再審' % args.book
    mdir = _resolve(args.materials)
    if not os.path.isdir(mdir):
        raise SystemExit('找不到材料目錄：' + mdir)
    outdir = _resolve(args.out) if args.out else mdir
    rep = os.path.join(mdir, '回覆')
    os.makedirs(outdir, exist_ok=True)

    metas = []
    for f in sorted(os.listdir(mdir)):
        if not f.endswith('.json') or f.startswith('_') or f.startswith('索引'):
            continue
        try:
            d = json.load(io.open(os.path.join(mdir, f), encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get('key') or not d.get('units'):
            continue
        if args.book and d.get('book') != args.book:
            continue
        metas.append(d)

    plan = {'generated': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'materials': _rel(mdir), 'book': args.book or '',
            'packs': {}, 'fix': {}, 'pass': [], 'abnormal': {},
            'pending': [], 'unattributed': {}, 'bisect': [],
            'bisect_skipped': [], 'stats': {}}
    n_fix = n_pass = n_ok = 0
    for meta in metas:
        key = meta['key']
        units = meta.get('units') or []
        reply_path = os.path.join(rep, key + '_回.txt')
        status, reason, rt, items = _classify(reply_path, meta, key)
        if status == 'pending':
            plan['pending'].append(key)
            plan['packs'][key] = {'units': len(units), 'status': 'pending'}
            continue
        if status == 'abnormal':
            plan['abnormal'][key] = reason
            plan['packs'][key] = {'units': len(units), 'status': 'abnormal',
                                  'reason': reason}
            _write_abnormal(reply_path, key, reason, rt, args.dry_run)
            if args.bisect and len(units) >= max(2, args.min_units):
                bdir = (_resolve(args.bisect_out) if args.bisect_out
                        else os.path.join(mdir, '_bisect'))
                os.makedirs(bdir, exist_ok=True)
                kids = _bisect(meta, bdir, args.dry_run)
                if kids:
                    plan['bisect'].append({'parent': key, 'reason': reason,
                                           'children': kids})
                else:
                    plan['bisect_skipped'].append(key)
            elif args.bisect:
                plan['bisect_skipped'].append(key)
            continue
        # ok
        n_ok += 1
        per = {}
        for it in items:
            per.setdefault(it['n'], []).append(it)
        ulist = units
        for no, its in sorted(per.items()):
            ukey = ulist[no - 1]['key']
            ck = '%s__%s' % (meta.get('book_id') or meta.get('book') or '', ukey)
            plan['fix'][ck] = {'pack': key, 'no': no, 'unit_key': ukey,
                               'book_id': meta.get('book_id') or '', 'items': its}
            n_fix += 1
        for i, u in enumerate(ulist, 1):
            if i not in per:
                plan['pass'].append('%s__%s'
                                    % (meta.get('book_id') or meta.get('book') or '',
                                       u['key']))
                n_pass += 1
        plan['packs'][key] = {'units': len(units), 'covered': len(units),
                              'fix': len(per), 'pass': len(units) - len(per),
                              'status': 'ok'}
    # 子包（--bisect）回覆若已存在，合併回母計畫：fix 指回母 pack 的 unit no
    bdir = (_resolve(args.bisect_out) if args.bisect_out
            else os.path.join(mdir, '_bisect'))
    if args.bisect and os.path.isdir(bdir):
        parent_units = {m['key']: [u.get('key') for u in (m.get('units') or [])]
                        for m in metas}
        book_of_pack = {m['key']: (m.get('book_id') or m.get('book') or '')
                        for m in metas}
        merged = []
        for f in sorted(os.listdir(bdir)):
            if not f.endswith('.json') or f.startswith('_'):
                continue
            try:
                cm = json.load(io.open(os.path.join(bdir, f), encoding='utf-8'))
            except Exception:
                continue
            child_key = cm.get('key') or f[:-5]
            pk = cm.get('parent') or ''
            if pk not in parent_units:
                continue
            st, rs, _rt, its = _classify(os.path.join(bdir, '回覆', child_key + '_回.txt'),
                                         cm, child_key)
            if st == 'ok':
                per_c = {}
                for it in its:
                    per_c.setdefault(it['n'], []).append(it)
                for no, items_c in per_c.items():
                    ukey = (cm.get('units') or [])[no - 1].get('key')
                    if ukey not in parent_units[pk]:
                        continue
                    pno = parent_units[pk].index(ukey) + 1
                    bid = book_of_pack.get(pk, '')
                    ck = '%s__%s' % (bid, ukey)
                    plan['fix'][ck] = {'pack': pk, 'no': pno, 'unit_key': ukey,
                                       'book_id': bid, 'items': items_c,
                                       'via_bisect': child_key}
                    if ck in plan['pass']:
                        plan['pass'].remove(ck)
                for i, u in enumerate(cm.get('units') or [], 1):
                    ck = '%s__%s' % (book_of_pack.get(pk, ''), u.get('key'))
                    if i not in per_c and ck not in plan['pass']:
                        plan['pass'].append(ck)
                merged.append(child_key)
            elif st == 'abnormal':
                plan['abnormal'][child_key] = rs
        if merged:
            plan['bisect_merged'] = merged
    _fix_n = len(plan['fix'])
    _pass_n = len(plan['pass'])
    _tot = _fix_n + _pass_n
    plan['stats'] = {'packs': len(metas), 'ok': n_ok,
                     'abnormal': len(plan['abnormal']),
                     'pending': len(plan['pending']),
                     'units_fix': _fix_n, 'units_pass': _pass_n,
                     'fix_ratio': round((_fix_n / _tot), 4) if _tot else 0.0}
    print('再審拆回：pack %d（成功 %d、異常 %d、待跑 %d）'
          % (len(metas), n_ok, len(plan['abnormal']), len(plan['pending'])))
    print('  FIX %d 單位、PASS %d 單位（FIX 比例 %.1f%%）'
          % (_fix_n, _pass_n, (100.0 * _fix_n / (_fix_n + _pass_n)) if (_fix_n + _pass_n) else 0))
    if plan['abnormal']:
        for k, v in list(plan['abnormal'].items())[:20]:
            print('  ⚠ %s：%s' % (k, v))
    if plan['bisect']:
        print('  已切半 %d 個異常檔 → %s'
              % (len(plan['bisect']),
                 _rel(_resolve(args.bisect_out) if args.bisect_out
                      else os.path.join(mdir, '_bisect'))))
    if args.dry_run:
        print('  （--dry-run：未改名、未寫計畫）')
        return
    pp = os.path.join(outdir, args.plan_name)
    io.open(pp, 'w', encoding='utf-8').write(
        json.dumps(plan, ensure_ascii=False, indent=1))
    if plan['abnormal']:
        io.open(os.path.join(outdir, '_異常清單.log'), 'w', encoding='utf-8').write(
            ''.join('%s\t%s\n' % (k, v) for k, v in plan['abnormal'].items()))
    print('  計畫 → %s' % _rel(pp))


if __name__ == '__main__':
    main()
