# -*- coding: utf-8 -*-
"""五書定稿「原文標點邊界」全量檢查＋安全修補（不改漢字、不改譯文）。

檢查法（以 TXT/ 原檔為句讀權威；raw_start/raw_end 為漢字流位移）
------------------------------------------------------------------
1. 缺開頭：raw 第一個漢字前的**緊鄰**字元是 《「『（ 之一，
   而 source 開頭沒帶該字元 → 缺開頭。
2. 缺結尾：raw 最後一個漢字後的**緊鄰**字元是 。」』）〕 之一，
   而 source 結尾沒帶該字元 → 缺結尾。
3. 只安全修「緊鄰單一標點且能確定」者：
   - 該端 raw 的句讀段正好一個字元；
   - source 該端完全沒有標點（source 開頭／結尾即漢字）。
   其餘（緊鄰兩個以上標點、source 該端已有別的標點、漢字流不符、未定位）
   一律只列報告，不硬補。
4. 修補只動 source＋display_source＋端點 segment 的 source／display_source；
   同一筆的漢字序列與 translation 必須逐字不變（程式斷言）。
5. `--include-display-only` 另修「source 已正確、只有 display_source 被
   產生器截掉句末標點」的顯示層缺口（預設不修，見報告說明）。

用法
----
    python -X utf8 _src/scan_source_punct_boundary.py                 # 只掃描
    python -X utf8 _src/scan_source_punct_boundary.py --json X --md Y  # 出報告
    python -X utf8 _src/scan_source_punct_boundary.py --apply --json X --md Y
    python -X utf8 _src/scan_source_punct_boundary.py --apply --include-display-only
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [
    ('行事鈔', 'xingshichao'),
    ('戒疏', 'jieshu'),
    ('業疏', 'yeshu'),
    ('尼鈔', 'nicao'),
    ('義鈔', 'yichao'),
]
RAW = {
    '行事鈔': 'TXT/01_四分律刪繁補闕行事鈔.txt',
    '戒疏': 'TXT/02_四分律含注戒本疏.txt',
    '業疏': 'TXT/03_四分律刪補隨機羯磨疏.txt',
    '尼鈔': 'TXT/04_四分律比丘尼鈔.txt',
    '義鈔': 'TXT/05_四分律拾毗尼義鈔.txt',
}
HAN = re.compile(r'[\u4e00-\u9fff]')
OPEN = '《「『（'          # 題目指定的開頭候選
CLOSE = '。」』）〕'        # 題目指定的結尾候選
PUNCT = set('，。、；：？！「」『』（）〔〕《》〈〉【】…—()')
CLOSERS = set('，。、；：？！」』）〕》〉】…—)')
OPENERS = set('「『（〔《〈【…—(')


def han(s):
    return ''.join(HAN.findall(s or ''))


def lead(s):
    i = 0
    while i < len(s) and not ('\u4e00' <= s[i] <= '\u9fff'):
        i += 1
    return s[:i]


def tail(s):
    j = len(s)
    while j > 0 and not ('\u4e00' <= s[j - 1] <= '\u9fff'):
        j -= 1
    return s[j:]


def md5(s):
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()[:12]


class Corpus(object):
    def __init__(self, text):
        self.text = text
        self.pos = []
        ch = []
        for i, c in enumerate(text):
            if '\u4e00' <= c <= '\u9fff':
                ch.append(c)
                self.pos.append(i)
        self.ch = ''.join(ch)

    def run_before(self, p):
        i = p
        while i > 0 and self.text[i - 1] in PUNCT:
            i -= 1
        return self.text[i:p]

    def run_after(self, q):
        i = q + 1
        while i < len(self.text) and self.text[i] in PUNCT:
            i += 1
        return self.text[q + 1:i]

    def lead_adj(self, a):
        """本單位開頭該帶的 opening 段＝句讀段中最後一個 closing 之後。"""
        run = self.run_before(self.pos[a])
        last = -1
        for i, c in enumerate(run):
            if c in CLOSERS:
                last = i
        return run[last + 1:]

    def tail_adj(self, b):
        """本單位結尾該帶的 closing 段＝句讀段中第一個 opening 之前。"""
        run = self.run_after(self.pos[b - 1])
        first = len(run)
        for i, c in enumerate(run):
            if c in OPENERS:
                first = i
                break
        return run[:first]


def classify(book, rows, corpus):
    plans = []
    for r in rows:
        key = r.get('key') or '?'
        a = int(r.get('raw_start', -1) or -1)
        b = int(r.get('raw_end', -1) or -1)
        rec = {'book': book, 'key': key, 'vol': r.get('vol') or '',
               'a': a, 'b': b, 'status': '', 'open': None, 'close': None,
               'off_open': '', 'off_close': '', 'changes': [], 'notes': []}
        if not (0 <= a < b <= len(corpus.ch)):
            rec['status'] = 'unlocated'
            plans.append(rec)
            continue
        src = r.get('source') or ''
        if han(src) != corpus.ch[a:b]:
            rec['status'] = 'han_mismatch'
            plans.append(rec)
            continue
        rec['status'] = 'ok'
        la = corpus.lead_adj(a)
        ta = corpus.tail_adj(b)
        sl, st = lead(src), tail(src)
        if la:
            c = la[-1]
            ok = c in sl
            item = {'c': c, 'adj': la, 'src_lead': sl, 'ok': ok,
                    'missing': False, 'safe': False, 'reason': ''}
            if c in OPEN:
                if not ok:
                    item['missing'] = True
                    if sl == '' and la == c:
                        item['safe'] = True
                    else:
                        item['reason'] = 'multi' if len(la) > 1 else 'conflict'
                rec['open'] = item
            else:
                if not ok:
                    rec['off_open'] = c
                    rec['notes'].append('開頭規格外缺：%r' % c)
        if ta:
            c = ta[0]
            ok = c in st
            item = {'c': c, 'adj': ta, 'src_tail': st, 'ok': ok,
                    'missing': False, 'safe': False, 'reason': ''}
            if c in CLOSE:
                if not ok:
                    item['missing'] = True
                    if st == '' and ta == c:
                        item['safe'] = True
                    else:
                        item['reason'] = 'multi' if len(ta) > 1 else 'conflict'
                rec['close'] = item
            else:
                if not ok:
                    rec['off_close'] = c
                    rec['notes'].append('結尾規格外缺：%r' % c)
        plans.append(rec)
    return plans


def locate_seg(seg, row, corpus):
    a = int(row.get('raw_start', -1) or -1)
    b = int(row.get('raw_end', -1) or -1)
    sh = han(seg.get('source'))
    if not sh:
        return None
    q = corpus.ch.find(sh, a, b)
    if q < 0 or q + len(sh) > b:
        return None
    return q, q + len(sh)


def sync_field(r, field, c, where, rec):
    """在端點加一個字元；只動 source／display_source。"""
    if where == 'open':
        s = r.get(field)
        if not s:
            return
        if c in lead(s):
            return
        if lead(s) != '':
            rec['notes'].append('%s %s lead 非空，略過' % (field, where))
            return
        r[field] = c + s
        rec['changes'].append({'field': field, 'where': where, 'add': c,
                               'before': s[:20], 'after': r[field][:20]})
    else:
        s = r.get(field)
        if not s:
            return
        if c in tail(s):
            return
        if tail(s) != '':
            rec['notes'].append('%s %s tail 非空，略過' % (field, where))
            return
        r[field] = s + c
        rec['changes'].append({'field': field, 'where': where, 'add': c,
                               'before': s[-20:], 'after': r[field][-20:]})


def build_changes(book, rows, plans, corpus):
    for r, rec in zip(rows, plans):
        if rec['status'] != 'ok':
            continue
        op, cl = rec['open'], rec['close']
        op_safe = bool(op and op.get('safe'))
        cl_safe = bool(cl and cl.get('safe'))
        if not (op_safe or cl_safe):
            continue
        segs = r.get('segments') or []
        seg_first = seg_last = None
        if segs:
            loc = locate_seg(segs[0], r, corpus)
            if loc and loc[0] == rec['a']:
                seg_first = segs[0]
            loc = locate_seg(segs[-1], r, corpus)
            if loc and loc[1] == rec['b']:
                seg_last = segs[-1]
        if op_safe:
            sync_field(r, 'source', op['c'], 'open', rec)
            sync_field(r, 'display_source', op['c'], 'open', rec)
            if seg_first is not None:
                sync_field(seg_first, 'source', op['c'], 'open', rec)
                sync_field(seg_first, 'display_source', op['c'], 'open', rec)
        if cl_safe:
            sync_field(r, 'source', cl['c'], 'close', rec)
            sync_field(r, 'display_source', cl['c'], 'close', rec)
            if seg_last is not None:
                sync_field(seg_last, 'source', cl['c'], 'close', rec)
                sync_field(seg_last, 'display_source', cl['c'], 'close', rec)
    return plans


def count_display_only(rows, plans, corpus):
    """盤點：source 端點已正確，但 display_source／segment display 端點缺緊鄰單一標點。"""
    keys = []
    for r, rec in zip(rows, plans):
        if rec['status'] != 'ok':
            continue
        op, cl = rec['open'], rec['close']
        need = False
        if op and op['ok'] and len(op['adj']) == 1:
            c = op['c']
            ds = r.get('display_source')
            if ds and c not in lead(ds) and lead(ds) == '':
                need = True
            segs = r.get('segments') or []
            if segs:
                loc = locate_seg(segs[0], r, corpus)
                if loc and loc[0] == rec['a']:
                    sds = segs[0].get('display_source')
                    if sds and c not in lead(sds) and lead(sds) == '':
                        need = True
        if cl and cl['ok'] and len(cl['adj']) == 1:
            c = cl['c']
            ds = r.get('display_source')
            if ds and c not in tail(ds) and tail(ds) == '':
                need = True
            segs = r.get('segments') or []
            if segs:
                loc = locate_seg(segs[-1], r, corpus)
                if loc and loc[1] == rec['b']:
                    sds = segs[-1].get('display_source')
                    if sds and c not in tail(sds) and tail(sds) == '':
                        need = True
        if need:
            keys.append(r.get('key'))
    return keys


def display_only_fix(book, rows, plans, corpus):
    """source 已正確、只有 display_source／segment display 端點缺緊鄰單一標點。"""
    fixed = []
    for r, rec in zip(rows, plans):
        if rec['status'] != 'ok':
            continue
        op, cl = rec['open'], rec['close']
        if not ((op and op['ok']) or (cl and cl['ok'])):
            continue
        c_open = ''
        if op and op['ok'] and len(op['adj']) == 1:
            c_open = op['c']
        c_close = ''
        if cl and cl['ok'] and len(cl['adj']) == 1:
            c_close = cl['c']
        if not (c_open or c_close):
            continue
        touched = []
        sink = {'changes': touched, 'notes': []}
        if c_open:
            sync_field(r, 'display_source', c_open, 'open', sink)
            segs = r.get('segments') or []
            if segs:
                loc = locate_seg(segs[0], r, corpus)
                if loc and loc[0] == rec['a']:
                    sync_field(segs[0], 'display_source', c_open, 'open', sink)
        if c_close:
            sync_field(r, 'display_source', c_close, 'close', sink)
            segs = r.get('segments') or []
            if segs:
                loc = locate_seg(segs[-1], r, corpus)
                if loc and loc[1] == rec['b']:
                    sync_field(segs[-1], 'display_source', c_close, 'close', sink)
        if touched:
            fixed.append({'key': r.get('key'), 'n': len(touched),
                          'where': [t['where'] + ':' + t['add'] for t in touched]})
    return fixed


def summarize(plans, n_disp_only):
    st = dict(rows=len(plans), unlocated=0, han_mismatch=0,
              open_missing=0, open_safe=0, open_unsure=0,
              close_missing=0, close_safe=0, close_unsure=0,
              both_safe=0, fixed_rows=0, fixed_fields=0,
              off_open=0, off_close=0, display_only_rows=0,
              ok_open=0, ok_close=0)
    ex = {'open_safe': [], 'open_unsure': [], 'close_safe': [],
          'close_unsure': [], 'off': [], 'both': []}
    unsure = []
    off = []
    hanmis = []
    for rec in plans:
        k = rec['key']
        if rec['status'] == 'unlocated':
            st['unlocated'] += 1
            continue
        if rec['status'] == 'han_mismatch':
            st['han_mismatch'] += 1
            hanmis.append(k)
            continue
        op, cl = rec['open'], rec['close']
        if op:
            if op['ok']:
                st['ok_open'] += 1
            if op['missing']:
                st['open_missing'] += 1
                item = {'key': k, 'adj': op['adj'], 'src_lead': op['src_lead'],
                        'c': op['c'], 'reason': op['reason']}
                if op['safe']:
                    st['open_safe'] += 1
                    if len(ex['open_safe']) < 5:
                        ex['open_safe'].append(item)
                else:
                    st['open_unsure'] += 1
                    if len(ex['open_unsure']) < 5:
                        ex['open_unsure'].append(item)
                    unsure.append(dict(item, where='open'))
        if rec['off_open']:
            st['off_open'] += 1
            off.append({'key': k, 'where': 'open', 'c': rec['off_open'],
                        'adj': op['adj'] if op else '', 'src': op['src_lead'] if op else ''})
        if cl:
            if cl['ok']:
                st['ok_close'] += 1
            if cl['missing']:
                st['close_missing'] += 1
                item = {'key': k, 'adj': cl['adj'], 'src_tail': cl['src_tail'],
                        'c': cl['c'], 'reason': cl['reason']}
                if cl['safe']:
                    st['close_safe'] += 1
                    if len(ex['close_safe']) < 5:
                        ex['close_safe'].append(item)
                else:
                    st['close_unsure'] += 1
                    if len(ex['close_unsure']) < 5:
                        ex['close_unsure'].append(item)
                    unsure.append(dict(item, where='close'))
        if rec['off_close']:
            st['off_close'] += 1
            off.append({'key': k, 'where': 'close', 'c': rec['off_close'],
                        'adj': cl['adj'] if cl else '', 'src': cl['src_tail'] if cl else ''})
        if op and cl and op['safe'] and cl['safe']:
            st['both_safe'] += 1
            if len(ex['both']) < 5:
                ex['both'].append(k)
        if rec['changes']:
            st['fixed_rows'] += 1
            st['fixed_fields'] += len(rec['changes'])
    st['display_only_rows'] = n_disp_only
    return st, ex, unsure, off, hanmis


def load(book_id):
    p = os.path.join(B, '定稿', book_id + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    return p, rows


def apply_file(path, rows):
    stamp = time.strftime('%Y%m%d_%H%M%S')
    d, f = os.path.split(path)
    bak = os.path.join(d, '_舊_%s_before_punctboundary_%s.jsonl' % (f[:-6], stamp))
    shutil.copy2(path, bak)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, path)
    return bak


def snapshot(rows):
    snap = {}
    for r in rows:
        snap[r.get('key')] = {
            'tr': r.get('translation'),
            'seg': [(s.get('label'), s.get('translation'),
                     han(s.get('source')), han(r.get('source'))) for s in (r.get('segments') or [])],
            'han': han(r.get('source')),
            'len': len(r.get('source') or ''),
            'nseg': len(r.get('segments') or []),
        }
    return snap


def verify(rows, snap):
    errs = []
    for r in rows:
        k = r.get('key')
        s = snap.get(k)
        if s is None:
            errs.append('%s 新列' % k)
            continue
        if r.get('translation') != s['tr']:
            errs.append('%s 譯文變動' % k)
        if han(r.get('source')) != s['han']:
            errs.append('%s source 漢字變動' % k)
        if len(r.get('source') or '') < s['len']:
            errs.append('%s source 變短' % k)
        if len(r.get('segments') or []) != s['nseg']:
            errs.append('%s segment 數變動' % k)
        for i, seg in enumerate(r.get('segments') or []):
            if i >= len(s['seg']):
                break
            if seg.get('translation') != s['seg'][i][1]:
                errs.append('%s seg%d 譯文變動' % (k, i))
            if han(seg.get('source')) != s['seg'][i][2]:
                errs.append('%s seg%d source 漢字變動' % (k, i))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', action='append', choices=[b for _, b in BOOKS])
    ap.add_argument('--json', default='')
    ap.add_argument('--keys', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--include-display-only', dest='disp_only', action='store_true')
    args = ap.parse_args()
    books = args.book or [b for _, b in BOOKS]
    out = {'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
           'raw': {bk: RAW[bk] for bk, _ in BOOKS},
           'open_set': OPEN, 'close_set': CLOSE,
           'display_only_included': bool(args.disp_only),
           'applied': bool(args.apply),
           'books': {}, 'totals': {}, 'changes': []}
    tot = dict(rows=0, unlocated=0, han_mismatch=0, open_missing=0, open_safe=0,
               open_unsure=0, close_missing=0, close_safe=0, close_unsure=0,
               both_safe=0, fixed_rows=0, fixed_fields=0, off_open=0, off_close=0,
               display_only_rows=0, ok_open=0, ok_close=0)
    keys_fixed = {}
    tot_verify = 0
    for bk, bid in BOOKS:
        if bid not in books:
            continue
        path, rows = load(bid)
        corpus = Corpus(io.open(os.path.join(B, RAW[bk]), encoding='utf-8').read())
        snap = snapshot(rows)
        plans = classify(bk, rows, corpus)
        disp_keys = count_display_only(rows, plans, corpus)
        disp = []
        if args.disp_only:
            disp = display_only_fix(bk, rows, plans, corpus)
            plans = classify(bk, rows, corpus)
        build_changes(bk, rows, plans, corpus)
        errs = verify(rows, snap)
        tot_verify += len(errs)
        for e in errs[:10]:
            print('  VERIFY-ERR', bk, e)
        st, ex, unsure, off, hanmis = summarize(plans, len(disp_keys))
        st['fixed_display_only'] = len(disp)
        bak = ''
        if args.apply and (st['fixed_rows'] or st['fixed_display_only']):
            bak = os.path.relpath(apply_file(path, rows), B)
            _, rows2 = load(bid)
            errs2 = verify(rows2, snap)
            if errs2:
                raise SystemExit('寫檔後驗證失敗：%s' % errs2[:5])
            st['backup'] = bak
        out['books'][bk] = {'book_id': bid, 'file': '定稿/' + bid + '.jsonl',
                            'stats': st, 'examples': ex, 'unsure': unsure,
                            'off': off[:200], 'han_mismatch': hanmis,
                            'display_only_keys': disp_keys[:200],
                            'display_only': disp, 'backup': bak}
        for k, v in st.items():
            if k in tot and isinstance(v, int):
                tot[k] += v
        keys_fixed[bk] = [rec['key'] for rec in plans if rec['changes']]
        out['changes'].extend([{'book': bk, 'key': rec['key'], 'vol': rec['vol'],
                                'changes': rec['changes']}
                               for rec in plans if rec['changes']])
        print('%-6s rows=%4d unloc=%d hanmis=%d | open miss/safe/unsure=%d/%d/%d | '
              'close miss/safe/unsure=%d/%d/%d | fixed_rows=%d fields=%d | '
              'disp_only_scan=%d fixed=%d %s'
              % (bk, st['rows'], st['unlocated'], st['han_mismatch'],
                 st['open_missing'], st['open_safe'], st['open_unsure'],
                 st['close_missing'], st['close_safe'], st['close_unsure'],
                 st['fixed_rows'], st['fixed_fields'], st['display_only_rows'],
                 st['fixed_display_only'], ('backup=' + bak) if bak else ''))
    out['totals'] = tot
    out['keys_fixed'] = keys_fixed
    out['verify_errors'] = tot_verify
    if args.keys:
        p = os.path.join(B, args.keys.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
            for bk, bid in BOOKS:
                ks = keys_fixed.get(bk) or []
                if not ks:
                    continue
                f.write('# %s（%d）\n' % (bk, len(ks)))
                for k in ks:
                    f.write(k + '\n')
        print('keys ->', p)
    if args.json:
        p = os.path.join(B, args.json.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
        print('json ->', p)
    print('TOTALS', json.dumps(tot, ensure_ascii=False))
    print('VERIFY-ERRORS', tot_verify)
    return 0


if __name__ == '__main__':
    sys.exit(main())
