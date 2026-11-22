# -*- coding: utf-8 -*-
"""再審套用：只替換 FIX 單位，其餘從原定稿逐筆複製，產 定稿_v2/<book>.jsonl。

安全設計：
  - 只讀 `定稿/<book>.jsonl`，絕不寫入 `定稿/`、`docs/`。
  - 未列入 FIX 的單位逐筆原樣輸出（不重排、不改欄位）。
  - 套用前驗證：
      1. `source == raw`（以 TXT_句讀校定 漢字流；資持記無可用底本 → 標未驗、需人工）
      2. 段別對位（回覆段數／標籤須與定稿 parts 一致，否則退回不套用）
      3. `norm.normalize` 正規化
      4. `qc_scan` 同構掃描（qc_scan.py 只有 CLI，故匯入其常數並在本次掃描）
      5. 幅度警報（新譯／原譯漢字比超出 ratio 只警示，不阻擋；--strict-qc 才阻擋 QC 警示）
  - 產出 `定稿_v2/<book>.jsonl` 與 `_再審變更對照.md`。

用法：
  python -X utf8 _src/apply_reaudit.py --book 業疏 \
      --materials 重作材料_長段/_再審材料/業疏 \
      --revise 重作材料_長段/_再審修訂/業疏 \
      --out 定稿_v2 --dry-run

  # 實際寫檔（會先擋掉既有輸出檔，除非 --force）
  python -X utf8 _src/apply_reaudit.py --book 業疏 ... --out 定稿_v2
"""
import argparse
import copy
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
import norm as NR  # noqa: E402
import qc_scan as QC  # noqa: E402  只取常數；逐段檢查在下方 _qc()

BOOKS = {
    '行事鈔': dict(id='xingshichao', raw='TXT_句讀校定/xingshichao.txt'),
    '戒疏': dict(id='jieshu', raw='TXT_句讀校定/jieshu.txt'),
    '業疏': dict(id='yeshu', raw='TXT_句讀校定/yeshu.txt'),
    '尼鈔': dict(id='nicao', raw='TXT_句讀校定/nicao.txt'),
    '義鈔': dict(id='yichao', raw='TXT_句讀校定/yichao.txt'),
    # 資持記：定稿 raw 位移與 TXT_句讀校定 不同制，無可驗底本。
    '資持記': dict(id='zhichi', raw=''),
}
PLAN_NAME = '_再審拆回_計畫.json'
LABS = ('疏文', '記文', '鈔文', '律文', '註文', '序文', '記序')
_LAB_RE = re.compile(r'(?m)^\s*(?:\*\*)?【(疏文|記文|鈔文|律文|註文|序文|記序)】(?:\*\*)?\s*')
_NUM_LEAD = re.compile(r'^\s*\[\s*\d{1,3}\s*\]\s*')
_LAB_HEAD = re.compile(r'^【(?:疏文|記文|鈔文|律文|註文|序文|記序)】\s*')
FENCE_RE = re.compile(r'(?m)^\s*```[a-zA-Z]*\s*$')
SIMP_BAD = ('达', '没', '时', '精准', '颗', '过', '与', '现', '实', '际', '种', '样', '动',
            '学', '觉', '见', '观', '识', '论', '证', '众', '问', '这', '为', '应', '经',
            '说', '义', '体', '归', '无', '还', '对', '发', '个', '们', '么', '护', '卫',
            '断', '灭', '尽', '离', '广', '严', '华', '乐', '礼', '处', '复', '单', '双',
            '当', '该', '传', '记', '书', '门', '从', '来')


def _resolve(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


def _rel(p):
    try:
        return os.path.relpath(p, B)
    except ValueError:
        return p


def _han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s or ''))


_META_CACHE = {}


def _unit_meta(mdir, pack_key, key):
    """取材料 json 內該 unit（供比對定稿是否已更新）。"""
    if not pack_key:
        return None
    if pack_key not in _META_CACHE:
        p = os.path.join(mdir, pack_key + '.json')
        _META_CACHE[pack_key] = (json.load(io.open(p, encoding='utf-8'))
                                 if os.path.exists(p) else {})
    d = _META_CACHE[pack_key]
    for u in d.get('units') or []:
        if u.get('key') == key:
            return u
    return None


def _stale_reason(meta_u, row, parts):
    """材料與現定稿逐段比對；不一致即退回（定稿可能在材料產出後被更新）。"""
    if not meta_u:
        return '找不到材料單位（材料與定稿不對應）'
    cur_src = _han(row.get('source', ''))
    if meta_u.get('src_hash') and meta_u['src_hash'] != _md5(cur_src):
        return '材料原文與現定稿不符（定稿已更新）'
    mp = meta_u.get('parts') or []
    if len(mp) != len(parts):
        return '材料段數與現定稿不符（定稿已更新）'
    for a, b in zip(mp, parts):
        if a.get('lab') != b['lab']:
            return '材料段別與現定稿不符（定稿已更新）'
        if (a.get('orig') or '') != (b['orig'] or ''):
            return '材料原文與現定稿不符（定稿已更新）'
        if _LAB_HEAD.sub('', a.get('tr') or '') != _LAB_HEAD.sub('', b['tr'] or ''):
            return '材料現譯與現定稿不符（定稿已更新，請重產材料）'
    return ''


def _md5(s):
    import hashlib
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()[:12]


def _load_raw(book):
    p = BOOKS[book].get('raw')
    if not p:
        return None, ''
    fp = os.path.join(B, p.replace('/', os.sep))
    if not os.path.exists(fp):
        return None, ''
    return _han(io.open(fp, encoding='utf-8').read()), p


# ---------------------------------------------------------------- 回覆解析
def _split_labeled(rt):
    """把「【疏文】…【記文】…」切成 [(lab, body)]；無標籤回 []。"""
    rt = FENCE_RE.sub('', rt or '')
    ms = list(_LAB_RE.finditer(rt))
    if not ms:
        return []
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(rt)
        body = rt[m.end():end]
        for cut in ('\n【必改硬傷】', '\n【可斟酌微瑕】', '\n【備註】', '\n【附註】'):
            if cut in body:
                body = body.split(cut)[0]
        out.append((m.group(1), _NUM_LEAD.sub('', body.strip()).strip()))
    return out


def _parse_reply(rt, parts):
    """回傳 (list[str] 對應 parts) 或 (None, 原因)。"""
    blocks = _split_labeled(rt)
    labs = [p.get('lab', '') for p in parts]
    if not blocks:
        body = FENCE_RE.sub('', rt or '').strip()
        for cut in ('【必改硬傷】', '【可斟酌微瑕】', '【分段核驗表】'):
            if cut in body:
                body = body.split(cut)[0]
        body = _NUM_LEAD.sub('', body.strip()).strip()
        if len(parts) == 1 and body:
            return [body], ''
        if len(parts) > 1:
            return None, '回覆無段別標籤（需 %s）' % '／'.join('【%s】' % x for x in labs)
        return None, '回覆為空'
    if len(blocks) != len(parts):
        return None, '段數不符（回覆 %d 段、定稿 %d 段）' % (len(blocks), len(parts))
    if len(parts) == 1 and len(blocks) == 1:
        # 單欄單位：模型可能依內容改標（如 JE-G14 定稿標「疏文」、實為記文），
        # 標籤不作為退回理由，只取正文；多欄仍嚴格比對順序。
        return [blocks[0][1].strip()], ''
    for (lab, _), want in zip(blocks, labs):
        if lab != want:
            return None, '段別順序不符（回覆【%s】、定稿【%s】）' % (lab, want)
    return [b.strip() for _, b in blocks], ''


# ---------------------------------------------------------------- 檢查
def _qc(src, out, src_disp=''):
    """qc_scan.py 的逐段同構掃描（該檔僅有 CLI，故於此重現其規則）。"""
    issues = []
    if not _han(out):
        return ['無實質譯文']
    for _a, _b, _n in (('「', '」', '「」'), ('『', '』', '『』'),
                       ('（', '）', '（）'), ('《', '》', '《》'), ('〔', '〕', '〔〕')):
        if out.count(_a) != out.count(_b):
            issues.append(_n + ' 未成對')
    if re.search(r'[（(]\s*[）)]', out):
        issues.append('殘留空括號（）')
    if 'http' in out:
        issues.append('殘留網址')
    if re.search(r'〔[^〕]*(?:據|按|考|校)[^〕]*〕', out):
        issues.append('〔〕內疑含校勘按語')
    if 'PASS_A' in out:
        issues.append('殘留 PASS_A 標記')
    if re.search(r'【(?:前|後)文背景|【分段核驗表】|【必改硬傷】|〔定稿殘留', out):
        issues.append('殘留材料區塊標記')
    if re.search(r'(?m)^\s*\d+[.、]\s', out):
        issues.append('殘留數字條列')
    if re.search(r'(?:local_search|web_search|web_fetch)\s*\(', out):
        issues.append('殘留工具呼叫字面')
    if re.search(r'(?m)^\s*(?:以下為.{0,16}整合|以下為整合|最終定稿白話版|完整修正版)', out):
        issues.append('殘留整合說明')
    if re.search(r'《(?:四分|十誦|五分|僧祇|摩訶僧祇)》', out):
        issues.append('律名簡稱未補「律」字')
    _labs = re.findall(r'(?m)^【(疏文|記文|鈔文|律文|註文|序文|記序)】', out)
    if any(_labs.count(x) > 1 for x in set(_labs)):
        issues.append('殘留重複欄位標籤')
    for _q in re.findall(r'[「『]([^」』]{8,})[」』]', out):
        if (len(QC.HAN.findall(_q)) >= 10
                and re.search(r'[的了著嗎呢吧]', _q)
                and re.search(r'[乎者也矣焉哉]', _q)):
            issues.append('引號內疑半文半白')
            break
    _out_noquote = re.sub(r'[「『][^」』]*[」』]', '', out)
    for _bad, _good in QC.BAD_VAR.items():
        if _bad in _out_noquote:
            issues.append('異體字 %s' % _bad)
            break
    _simp = re.sub(r'[「『][^」』]*[」』]', '', out)
    if any(_b in _simp for _b in SIMP_BAD):
        issues.append('殘留簡體字')
    sh = len(QC.HAN.findall(src))
    oh = len(QC.HAN.findall(out))
    if sh >= 10 and oh < sh * 0.4:
        issues.append('嚴重縮水（疑漏譯）%d→%d' % (sh, oh))
    if 10 <= sh <= 75 and oh > sh * 2.4:
        issues.append('短文膨脹 %d→%d' % (sh, oh))
    _disp_notes = len(re.findall(r'〔[^〕]{2,}〕', src_disp or ''))
    _src_notes = max(0, src.count('（') + src.count('(') + src.count('〔')
                     + _disp_notes - out.count('〔'))
    _out_pars = [x.strip() for x in re.findall(r'[（(]([^）)]*)[）)]', out)
                 if not re.fullmatch(r'[一二三四五六七八九十百千\d]+', x.strip())
                 and not re.fullmatch(r'[^，。；]{0,8}反', x.strip())]
    if len(_out_pars) > _src_notes:
        issues.append('疑自加解說括號（譯 %d＞原 %d）' % (len(_out_pars), _src_notes))
    return issues


def _parts_of(row):
    segs = [s for s in (row.get('segments') or []) if (s.get('source') or s.get('translation'))]
    if segs:
        return [{'lab': s.get('label') or row.get('label') or '鈔文',
                 'orig': s.get('source') or '',
                 'tr': s.get('translation') or '',
                 'display': s.get('display_source') or row.get('display_source') or ''} for s in segs]
    return [{'lab': row.get('label') or '鈔文', 'orig': row.get('source') or '',
             'tr': row.get('translation') or '',
             'display': row.get('display_source') or ''}]


def _part_spans(row, raw_h):
    """回傳 parts 的 raw 起迄（累加漢字長；與 mk_reaudit_materials 同法）。"""
    a, b = int(row.get('raw_start', -1) or -1), int(row.get('raw_end', -1) or -1)
    parts = _parts_of(row)
    hs = [_han(p['orig']) for p in parts]
    if raw_h is None:
        return [(None, None) for _ in parts]
    unit_h = _han(row.get('source', ''))
    if 0 <= a < b <= len(raw_h) and raw_h[a:b] == unit_h \
            and sum(len(x) for x in hs) == len(unit_h):
        out, cur = [], a
        for h in hs:
            out.append((cur, cur + len(h)))
            cur += len(h)
        return out
    out, cur = [], max(0, a)
    for h in hs:
        q = raw_h.find(h, max(0, a - 40), b if b > a else len(raw_h)) if h else -1
        if q >= 0:
            out.append((q, q + len(h)))
            cur = q + len(h)
        else:
            out.append((cur, cur + len(h)))
            cur += len(h)
    return out


def _rebuild(old_tr, parts, new_trs):
    labs = [p['lab'] for p in parts]
    if len(new_trs) > 1:
        has_lab = any(('【%s】' % lab) in (old_tr or '') for lab in labs)
        if has_lab:
            return '\n'.join('【%s】%s' % (lab, tr) for lab, tr in zip(labs, new_trs))
        return '\n\n'.join(new_trs)
    tr = new_trs[0]
    prefix = re.match(r'^\s*(【[^】]+】)\s*', old_tr or '')
    if prefix and prefix.group(1) in ('【%s】' % x for x in LABS):
        sep = '\n' if re.match(r'^\s*【[^】]+】\s*\n', old_tr or '') else ''
        return '%s%s%s' % (prefix.group(1), sep, tr)
    return tr


def _guard_out(out, book):
    od = os.path.abspath(out)
    base = os.path.abspath(B)
    for bad in ('定稿', 'docs'):
        b = os.path.join(base, bad)
        if od == b or od.startswith(b + os.sep):
            raise SystemExit('拒絕寫入 %s（本流程不得改 定稿／docs）' % bad)
    if od == base:
        raise SystemExit('拒絕寫入專案根目錄')
    return od


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser(
        description='再審套用：只替換 FIX 單位，其餘複製原定稿，產 定稿_v2（不呼叫 qwen）')
    ap.add_argument('--book', required=True, choices=list(BOOKS))
    ap.add_argument('--materials', default='',
                    help='再審材料目錄（預設 測試/重譯/<book>/_再審）')
    ap.add_argument('--plan', default='', help='拆回計畫（預設 <materials>/%s）' % PLAN_NAME)
    ap.add_argument('--revise', default='',
                    help='單段修訂材料目錄（預設 測試/重譯/<book>/_再審修訂）')
    ap.add_argument('--out', default='定稿_v2', help='輸出目錄（預設 定稿_v2）')
    ap.add_argument('--out-name', default='', help='輸出檔名（預設 <book_id>.jsonl）')
    ap.add_argument('--report', default='', help='對照報告路徑（預設 <out>/_再審變更對照.md）')
    ap.add_argument('--max-ratio', type=float, default=1.8, help='幅度上限（預設 1.8）')
    ap.add_argument('--min-ratio', type=float, default=0.55, help='幅度下限（預設 0.55）')
    ap.add_argument('--strict-qc', action='store_true', help='QC 有警示即退回不套用（不含幅度）')
    ap.add_argument('--strict-ratio', action='store_true', help='幅度超出 ±ratio 即退回（預設只警示）')
    ap.add_argument('--dry-run', action='store_true', help='只驗證與統計，不寫任何檔案')
    ap.add_argument('--force', action='store_true', help='允許覆寫既有輸出檔')
    args = ap.parse_args()

    bid = BOOKS[args.book]['id']
    out = _guard_out(_resolve(args.out), args.book)
    src_jsonl = os.path.join(B, '定稿', bid + '.jsonl')
    if not os.path.exists(src_jsonl):
        raise SystemExit('找不到定稿：' + src_jsonl)
    if not args.materials:
        args.materials = '測試/重譯/%s/_再審' % args.book
    if not args.revise:
        args.revise = '測試/重譯/%s/_再審修訂' % args.book
    mdir = _resolve(args.materials)
    plan_path = (_resolve(args.plan) if args.plan
                 else os.path.join(mdir, PLAN_NAME))
    if not os.path.exists(plan_path):
        raise SystemExit('找不到拆回計畫：' + plan_path)
    plan = json.load(io.open(plan_path, encoding='utf-8'))
    fix = plan.get('fix') or {}
    rep = os.path.join(_resolve(args.revise), '回覆')
    out_name = args.out_name or (bid + '.jsonl')
    dst = os.path.join(out, out_name)
    report = (_resolve(args.report) if args.report
              else os.path.join(out, '_再審變更對照.md'))
    if os.path.exists(dst) and not args.force and not args.dry_run:
        raise SystemExit('輸出檔已存在（%s）；請加 --force 或改用新目錄。' % dst)

    raw_h, raw_path = _load_raw(args.book)
    rows = [json.loads(x) for x in io.open(src_jsonl, encoding='utf-8') if x.strip()]
    by_key = {r.get('key'): r for r in rows}
    missing = [k for k in fix if k not in by_key]
    applied, blocked, pending = [], [], []
    new_rows = []
    for row in rows:
        key = row.get('key')
        if key not in fix:
            new_rows.append(row)
            continue
        info = fix[key]
        rp = os.path.join(rep, key + '_回.txt')
        if not os.path.exists(rp):
            pending.append((key, '缺修訂回覆'))
            new_rows.append(row)
            continue
        rt = io.open(rp, encoding='utf-8').read()
        parts = _parts_of(row)
        _segs = [s for s in (row.get('segments') or [])
                 if (s.get('source') or s.get('translation'))]
        if len(_segs) != len(parts):
            blocked.append((key, '段別結構不一致（segments %d、可譯 parts %d）'
                            % (len(_segs), len(parts))))
            new_rows.append(row)
            continue
        _why = _stale_reason(_unit_meta(mdir, info.get('pack'), key), row, parts)
        if _why:
            blocked.append((key, _why))
            new_rows.append(row)
            continue
        spans = _part_spans(row, raw_h)
        # source == raw 驗證
        raw_note = ''
        if raw_h is None:
            raw_note = 'raw 未驗（無底本）'
        else:
            a, b = int(row.get('raw_start', -1) or -1), int(row.get('raw_end', -1) or -1)
            if not (0 <= a < b <= len(raw_h) and raw_h[a:b] == _han(row.get('source', ''))):
                blocked.append((key, 'source≠raw（定稿定位與底本不符）'))
                new_rows.append(row)
                continue
            for p, (pa, pb) in zip(parts, spans):
                if pa is None or _han(p['orig']) != raw_h[pa:pb]:
                    raw_note = 'part 定位僅估算'
                    break
        new_trs, why = _parse_reply(rt, parts)
        if new_trs is None:
            blocked.append((key, why))
            new_rows.append(row)
            continue
        new_trs = [NR.normalize(t, p['orig']).strip() for t, p in zip(new_trs, parts)]
        if any(not _han(t) for t in new_trs):
            blocked.append((key, '回覆段別有空白譯文'))
            new_rows.append(row)
            continue
        flags = []
        ratio_flags = []
        old_han = sum(len(_han(p['tr'])) for p in parts)
        new_han = sum(len(_han(t)) for t in new_trs)
        ratio = (new_han / old_han) if old_han else 0.0
        if ratio and (ratio > args.max_ratio or ratio < args.min_ratio):
            ratio_flags.append('幅度 %.2f（%d→%d）' % (ratio, old_han, new_han))
        qc_flags = []
        for p, t in zip(parts, new_trs):
            qc_flags += _qc(p['orig'], t, p.get('display') or '')
        flags = qc_flags + ratio_flags
        if raw_note:
            flags.append(raw_note)
        # --strict-qc 只擋 QC；長度倍率另用 --strict-ratio（避免補漏譯被誤退）
        if ((qc_flags or raw_note) and args.strict_qc) or (
                ratio_flags and getattr(args, 'strict_ratio', False)):
            blocked.append((key, '；'.join(flags)))
            new_rows.append(row)
            continue
        nr = copy.deepcopy(row)
        nr['translation'] = _rebuild(row.get('translation', ''), parts, new_trs)
        segs = nr.get('segments') or []
        if segs:
            if len(segs) != len(new_trs):
                blocked.append((key, '段數不符：segments %d、回覆 %d' % (len(segs), len(new_trs))))
                new_rows.append(row)
                continue
            for s, t in zip(segs, new_trs):
                s['translation'] = t
        elif parts:
            nr['label'] = parts[0]['lab']
        nr['revised'] = True
        new_rows.append(nr)
        applied.append({
            'key': key, 'vol': row.get('vol', ''), 'chunk': row.get('chunk', ''),
            'labs': [p['lab'] for p in parts],
            'old': old_han, 'new': new_han, 'ratio': ratio,
            'flags': flags,
            'n_fix': len(info.get('items') or []),
        })

    # 驗證輸出結構
    if len(new_rows) != len(rows):
        raise SystemExit('內部錯誤：輸出筆數 %d ≠ 原定稿 %d' % (len(new_rows), len(rows)))
    keys_out = [r.get('key') for r in new_rows]
    if keys_out != [r.get('key') for r in rows]:
        raise SystemExit('內部錯誤：單位順序改變')

    print('再審套用（%s）：定稿 %d 單位；FIX %d；套用 %d、退回 %d、待修 %d'
          % (args.book, len(rows), len(fix), len(applied), len(blocked), len(pending)))
    for row in applied[:10]:
        print('  ✅ %s %s %s %d→%d 字%s'
              % (row['key'], row['vol'], '／'.join(row['labs']), row['old'],
                 row['new'], ('；' + '；'.join(row['flags'])) if row['flags'] else ''))
    for k, why in blocked[:10]:
        print('  ⛔ %s：%s' % (k, why))
    if args.dry_run:
        print('  （--dry-run：未寫入 %s）' % _rel(dst))
        return

    os.makedirs(out, exist_ok=True)
    with io.open(dst, 'w', encoding='utf-8') as f:
        for r in new_rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # ---- 對照報告 ----
    L = ['# 再審套用變更對照（%s）' % args.book, '',
         '- 來源定稿：%s（%d 單位）' % (_rel(src_jsonl), len(rows)),
         '- 輸出定稿：%s（%d 單位）' % (_rel(dst), len(new_rows)),
         '- 拆回計畫：%s' % _rel(plan_path),
         '- 原文底本：%s' % (raw_path or '（無，raw 驗證 unavailable）'),
         '- 套用 %d／退回 %d／待修 %d（FIX 共 %d）'
         % (len(applied), len(blocked), len(pending), len(fix)), '',
         '## 套用明細', '',
         '| # | key | 卷 | 段別 | 原譯字數 | 新譯字數 | 幅度 | 硬傷項 | QC／備註 |',
         '|--:|:--|:--|:--|--:|--:|--:|--:|:--|']
    for i, a in enumerate(applied, 1):
        L.append('| %d | %s | %s | %s | %d | %d | %.2f | %d | %s |'
                 % (i, a['key'], a['vol'], '／'.join(a['labs']), a['old'], a['new'],
                    a['ratio'], a['n_fix'], '；'.join(a['flags']) or '—'))
    L += ['', '## 未套用（退回）明細', '',
          '| key | 原因 |', '|:--|:--|']
    for k, why in blocked:
        L.append('| %s | %s |' % (k, why))
    if pending:
        L += ['', '## 待修（缺修訂回覆，保留原譯）', '',
              '| key | 原因 |', '|:--|:--|']
        for k, why in pending:
            L.append('| %s | %s |' % (k, why))
    if missing:
        L += ['', '## 計畫內有、定稿查無', '',
              '| key |', '|:--|']
        for k in missing:
            L.append('| %s |' % k)
    L += ['', '## 說明', '',
          '- 本檔只在 `--out` 寫出，未修改 `定稿/`、`docs/` 或任何網站檔。',
          '- 未列 FIX 的單位逐筆原樣複製（欄位、順序不變）。',
          '- 幅度＝新譯漢字／原譯漢字；超出 ±ratio 僅警示，`--strict-qc` 才退回。',
          '- QC 為 `qc_scan.py` 規則的同構掃描（該檔僅有 CLI，無可 import 的逐段函式）。']
    _rd = os.path.dirname(report)
    if _rd:
        os.makedirs(_rd, exist_ok=True)
    io.open(report, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('  輸出 → %s' % _rel(dst))
    print('  對照 → %s' % _rel(report))


if __name__ == '__main__':
    main()
