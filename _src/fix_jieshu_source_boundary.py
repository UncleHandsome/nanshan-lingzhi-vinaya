# -*- coding: utf-8 -*-
"""戒疏定稿 source 邊界修正（只補回被 trim 掉的邊界句讀，不改譯文）。

背景
----
`trim_jieshu_overlaps.py` 曾把 source 改成
    raw[mp[a]:mp[b-1]+1]
也就是「第一個漢字到最後一個漢字」的顯示切片，結果把緊貼邊界的
「」『』【】《》（）。！？，、；： 全部切掉。漢字流沒少，但網站
原文會少引號、書名號、句末標點。

本腳本
------
1. 以 `TXT_句讀校定/jieshu.txt` 為句讀底本（與 TXT/02 漢字、全文皆同）。
2. raw_start/raw_end 是「漢字流」位移，不動（除非漢字真有缺，本輪掃到 0 筆）。
3. 只把 source 的顯示邊界擴大到相鄰句讀：
   - 左：連續 opening 標記（「『【（《〔），但 segment 的【標籤】不併入。
   - 右：連續 closing／句末標記（」』】）》。！？，、；：》）。
4. row 有 segments 時，同步修 segment.source 的邊界句讀；不動 segment.translation。
5. 每筆 assert：新 source 漢字 == 原 raw_start:raw_end 漢字；顯示區間不與前後列重疊。
6. `--apply` 才寫檔；預設 dry-run。

用法
----
    python -X utf8 _src/fix_jieshu_source_boundary.py
    python -X utf8 _src/fix_jieshu_source_boundary.py --apply
    python -X utf8 _src/fix_jieshu_source_boundary.py --plan 重作材料_長段/戒疏source邊界修正_plan.json
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
RAW = os.path.join(B, 'TXT_句讀校定', 'jieshu.txt')
JSONL = os.path.join(B, '定稿', 'jieshu.jsonl')

HAN = re.compile(r'[\u4e00-\u9fff]')
LAB = re.compile(r'^(?:【[^】]+】)+')
OPEN = '「『【（《〔'
RIGHT = '」』】）》。！？，、；：》'


def han(s):
    return ''.join(HAN.findall(s or ''))


def md5(s):
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()[:12]


class Corpus:
    def __init__(self, text):
        self.text = text
        self.ch = []
        self.pos = []
        for i, c in enumerate(text):
            if '\u4e00' <= c <= '\u9fff':
                self.ch.append(c)
                self.pos.append(i)
        self.ch = ''.join(self.ch)

    def left(self, i):
        """i 是第一個漢字的顯示位移；往前吃連續 opening 標記。"""
        lim = 0
        while i > lim and self.text[i - 1] in OPEN:
            i -= 1
        return i

    def right(self, i):
        """i 是最後一個漢字的顯示位移 + 1；往後吃連續 closing／句末標記。"""
        while i < len(self.text) and self.text[i] in RIGHT:
            i += 1
        return i

    def disp_slice(self, a, b, skip_label=False):
        """回傳 (l, r, text)，a/b 是漢字流區間。"""
        l = self.left(self.pos[a])
        r = self.right(self.pos[b - 1] + 1)
        if skip_label:
            # 若左擴張只吃到 row 起始的【標籤】，不要把它併進 segment 本文
            pre = self.text[l:self.pos[a]]
            if pre == '【':
                l = self.pos[a]
            elif pre.startswith('【') and pre.endswith('】'):
                l = pre.rfind('】') + 1
                l = self.pos[a] - (len(pre) - l)
        return l, r, self.text[l:r]

    def disp_of_han(self, q, e):
        return self.pos[q], self.pos[e - 1] + 1


def split_label(text):
    m = LAB.match(text or '')
    if not m:
        return '', text or ''
    return m.group(0), (text or '')[m.end():]


def locate_seg(ch, body_han, a, b, cur):
    """把 segment 本文漢字定位到 row 的漢字區間內。"""
    if not body_han:
        return None
    for lo in (cur, a, max(0, a - 8)):
        q = ch.find(body_han, lo)
        if q >= 0 and q + len(body_han) <= b:
            return q
    return None


def build_plan():
    rows = [json.loads(x) for x in io.open(JSONL, encoding='utf-8') if x.strip()]
    corpus = Corpus(io.open(RAW, encoding='utf-8').read())
    errors = []
    row_changes = []
    seg_changes = []
    seg_flagged = []
    seg_internal = 0
    unchanged_rows = []
    stat = {
        'rows': len(rows),
        'row_han_mismatch': 0,
        'row_base_mismatch': 0,
        'lead_quote': 0,
        'lead_bracket': 0,
        'lead_book': 0,
        'lead_other': 0,
        'tail_period': 0,
        'tail_quote': 0,
        'tail_question': 0,
        'tail_excl': 0,
        'tail_comma': 0,
        'tail_other': 0,
        'both': 0,
        'unchanged': 0,
    }
    key_order = {r['key']: i for i, r in enumerate(rows)}

    for r in rows:
        key = r.get('key', '?')
        a, b = int(r.get('raw_start', -1) or -1), int(r.get('raw_end', -1) or -1)
        src = (r.get('source') or '').strip()
        sh = han(src)
        if not (0 <= a < b <= len(corpus.ch)) or corpus.ch[a:b] != sh:
            stat['row_han_mismatch'] += 1
            errors.append((key, 'row source 漢字 != raw 區間', a, b, len(sh)))
            continue
        base = corpus.text[corpus.pos[a]:corpus.pos[b - 1] + 1]
        l, rr, new_src = corpus.disp_slice(a, b)
        already = (src == new_src)          # 已修過：可重跑，不會重複加標點
        if src != base and not already:
            stat['row_base_mismatch'] += 1
            errors.append((key, 'row source != 現有 raw 切片', repr(src[:16]), repr(base[:16])))
            continue
        pre = corpus.text[l:corpus.pos[a]]
        suf = corpus.text[corpus.pos[b - 1] + 1:rr]
        if han(new_src) != sh:
            errors.append((key, '新 source 漢字 != raw 漢字', repr(new_src[:16])))
            continue
        if already:
            # 已是擴大後的切片：不列為本次變更，但 segments 仍要檢查
            pre = suf = ''
        if pre or suf:
            cls_l = cls_r = ''
            if pre:
                if pre.lstrip(OPEN) == '':
                    if '「' in pre:
                        cls_l = 'lead_quote'
                    elif '『' in pre:
                        cls_l = 'lead_quote'
                    elif '【' in pre:
                        cls_l = 'lead_bracket'
                    elif '《' in pre:
                        cls_l = 'lead_book'
                    else:
                        cls_l = 'lead_other'
                    stat[cls_l] += 1
                else:
                    stat['lead_other'] += 1
                    cls_l = 'lead_other'
            if suf:
                if '。' in suf:
                    cls_r = 'tail_period'
                elif '」' in suf or '』' in suf or '】' in suf:
                    cls_r = 'tail_quote'
                elif '？' in suf:
                    cls_r = 'tail_question'
                elif '！' in suf:
                    cls_r = 'tail_excl'
                elif any(c in suf for c in '，、；：'):
                    cls_r = 'tail_comma'
                else:
                    cls_r = 'tail_other'
                stat[cls_r] += 1
            if pre and suf:
                stat['both'] += 1
            row_changes.append({
                'key': key,
                'raw_start': a,
                'raw_end': b,
                'disp_start_before': corpus.pos[a],
                'disp_end_before': corpus.pos[b - 1] + 1,
                'disp_start_after': l,
                'disp_end_after': rr,
                'prefix': pre,
                'suffix': suf,
                'class': (cls_l + '+' + cls_r).strip('+'),
                'before': src,
                'after': new_src,
            })
        else:
            unchanged_rows.append(key)

        # ---- segments ----
        segs = r.get('segments') or []
        cur = a
        for si, s in enumerate(segs):
            label_pre, body = split_label((s.get('source') or '').strip())
            bh = han(body)
            if not bh:
                continue
            q = locate_seg(corpus.ch, bh, a, b, cur)
            if q is None:
                seg_flagged.append((key, si, 'segment 定位不到', repr(body[:16])))
                continue
            e = q + len(bh)
            cur = e
            l2 = corpus.left(corpus.pos[q])
            # 內層 segment 開頭的【是行內段標，不是本文
            pre2 = corpus.text[l2:corpus.pos[q]]
            if pre2 == '【' or (pre2.startswith('【') and pre2.endswith('】')):
                l2 = corpus.pos[q]
            r2 = corpus.right(corpus.pos[e - 1] + 1)
            new_body = corpus.text[l2:r2]
            if new_body == body:
                continue
            if han(new_body) != bh:
                seg_flagged.append((key, si, 'segment 新本文漢字不符', repr(new_body[:16])))
                continue
            # 只允許本文前後補句讀，不改本文內部。body 可能帶 [1]／空白等
            # 材料標記，故用 find 定位，且要求本文完整出現一次。
            idx = new_body.find(body)
            if idx < 0 or new_body.find(body, idx + 1) >= 0:
                seg_internal += 1
                continue
            add_pre = new_body[:idx]
            add_suf = new_body[idx + len(body):]
            if add_pre.startswith((' ', '\n', '\u3000')) or add_suf.endswith((' ', '\n', '\u3000')):
                seg_internal += 1
                continue
            # 段首【是行內段標，不併入 segment 本文
            if add_pre and add_pre.strip() == '【':
                add_pre = ''
                new_body = body + add_suf
            if not add_pre and not add_suf:
                seg_internal += 1
                continue
            seg_changes.append({
                'key': key, 'seg': si, 'label': s.get('label'),
                'before': s.get('source') or '',
                'after': label_pre + new_body,
                'add_pre': add_pre, 'add_suf': add_suf,
            })

    # ---- overlap 檢查（漢字流 + 顯示切片）----
    by_pos = sorted(rows, key=lambda r: (int(r.get('raw_start', -1) or -1), r.get('key', '')))
    han_ov = 0
    disp_ov = 0
    prev_end = -1
    prev_disp_end = -1
    for r in by_pos:
        a, b = int(r['raw_start']), int(r['raw_end'])
        if a < prev_end:
            han_ov += b - max(a, prev_end)
        prev_end = max(prev_end, b)
        l, rr, _ = corpus.disp_slice(a, b)
        if l < prev_disp_end:
            disp_ov += 1
            errors.append((r['key'], '顯示切片與前列重疊', prev_disp_end, l))
        prev_disp_end = max(prev_disp_end, rr)

    stat['unchanged'] = len(unchanged_rows)
    stat['row_changes'] = len(row_changes)
    stat['seg_changes'] = len(seg_changes)
    stat['seg_flagged'] = len(seg_flagged)
    stat['seg_internal'] = seg_internal
    stat['han_overlap'] = han_ov
    stat['disp_overlap'] = disp_ov
    return {
        'rows': rows,
        'corpus': corpus,
        'row_changes': row_changes,
        'seg_changes': seg_changes,
        'seg_flagged': seg_flagged,
        'unchanged_rows': unchanged_rows,
        'errors': errors,
        'stat': stat,
    }


def verify(rows, corpus):
    """回寫後的硬檢查。"""
    out = {'rows': len(rows), 'han_mismatch': 0, 'unlocated': 0, 'han_overlap': 0,
           'disp_overlap': 0, 'empty_tr': 0, 'bad_han_source': 0}
    cover = [0] * len(corpus.ch)
    spans = []
    for r in rows:
        a, b = int(r.get('raw_start', -1) or -1), int(r.get('raw_end', -1) or -1)
        if not (0 <= a < b <= len(corpus.ch)):
            out['unlocated'] += 1
            continue
        if corpus.ch[a:b] != han(r.get('source')):
            out['han_mismatch'] += 1
        if not (r.get('translation') or '').strip():
            out['empty_tr'] += 1
        for i in range(a, b):
            cover[i] += 1
        l, rr, _ = corpus.disp_slice(a, b)
        spans.append((l, rr, r.get('key')))
    out['han_overlap'] = sum(1 for c in cover if c > 1)
    spans.sort()
    prev = -1
    for l, rr, k in spans:
        if l < prev:
            out['disp_overlap'] += 1
        prev = max(prev, rr)
    return out


def apply_plan(plan):
    rows = plan['rows']
    corpus = plan['corpus']
    change_by_key = {c['key']: c for c in plan['row_changes']}
    seg_by = {}
    for c in plan['seg_changes']:
        seg_by.setdefault(c['key'], {})[c['seg']] = c
    tr_before = {r['key']: md5(r.get('translation')) for r in rows}
    seg_tr_before = {r['key']: md5(json.dumps([s.get('translation') for s in (r.get('segments') or [])],
                                              ensure_ascii=False)) for r in rows}
    for r in rows:
        key = r.get('key')
        if key in change_by_key:
            r['source'] = change_by_key[key]['after']
        for si, c in (seg_by.get(key) or {}).items():
            r['segments'][si]['source'] = c['after']

    # 譯文不得變
    for r in rows:
        assert md5(r.get('translation')) == tr_before[r['key']], ('translation changed', r['key'])
        assert md5(json.dumps([s.get('translation') for s in (r.get('segments') or [])],
                              ensure_ascii=False)) == seg_tr_before[r['key']], ('segment tr changed', r['key'])
        # segment source 漢字不得變
        for s in r.get('segments') or []:
            assert han(s.get('source'))

    stamp = time.strftime('%Y%m%d_%H%M%S')
    bak = os.path.join(B, '定稿', '_舊_jieshu_before_boundaryfix_%s.jsonl' % stamp)
    shutil.copy2(JSONL, bak)
    tmp = JSONL + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, JSONL)
    return bak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--plan', default='')
    args = ap.parse_args()
    plan = build_plan()
    st = plan['stat']
    print('rows', st['rows'])
    print('row_han_mismatch', st['row_han_mismatch'], 'row_base_mismatch', st['row_base_mismatch'])
    print('row_changes', st['row_changes'], 'unchanged', st['unchanged'])
    print('  lead_quote', st['lead_quote'], 'lead_bracket', st['lead_bracket'],
          'lead_book', st['lead_book'], 'lead_other', st['lead_other'])
    print('  tail_period', st['tail_period'], 'tail_quote', st['tail_quote'],
          'tail_question', st['tail_question'], 'tail_excl', st['tail_excl'],
          'tail_comma', st['tail_comma'], 'tail_other', st['tail_other'], 'both', st['both'])
    print('seg_changes', st['seg_changes'], 'seg_flagged', st['seg_flagged'],
          'seg_internal_diff', st['seg_internal'])
    print('han_overlap', st['han_overlap'], 'disp_overlap', st['disp_overlap'], 'errors', len(plan['errors']))
    for e in plan['errors'][:10]:
        print('  ERR', e)
    for e in plan['seg_flagged'][:10]:
        print('  SEGFLAG', e)

    if args.plan:
        d = {
            'stat': st,
            'row_changes': plan['row_changes'],
            'seg_changes': plan['seg_changes'],
            'seg_flagged': plan['seg_flagged'],
            'errors': plan['errors'],
        }
        p = os.path.join(B, args.plan.replace('/', os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=1) + '\n')
        print('plan ->', p)

    if not args.apply:
        print('dry-run；加 --apply 才寫入')
        return 0
    if plan['errors']:
        print('有 error，拒絕寫入')
        return 1
    bak = apply_plan(plan)
    print('backup', bak)
    rows = [json.loads(x) for x in io.open(JSONL, encoding='utf-8') if x.strip()]
    v = verify(rows, plan['corpus'])
    print('VERIFY', v)
    return 0 if all(v[k] == 0 for k in ('han_mismatch', 'unlocated', 'han_overlap', 'disp_overlap', 'empty_tr')) else 1


if __name__ == '__main__':
    sys.exit(main())
