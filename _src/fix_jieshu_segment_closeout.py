# -*- coding: utf-8 -*-
"""戒疏 segment 邊界收尾（只動指定 3 個 segment 的 source，不改譯文）。

本輪處理
--------
1. 01c_卷一上之一_0059
   segment.source = `四分戒本。`，row.source = `《四分戒本》`。
   raw 邊界是 `《四分戒本》者`；segment 掉了書名號、又多了一個 raw 沒有的
   `。`。以 row 的顯示切片回填；漢字不變。
2. 戒疏-G19
   segment.source 尾端是 `……也。\n　　【疏】「`：`【疏】` 是下一單元的
   段標，`「` 是下一句的開引號，兩者都不屬於本段譯文。只保留到 raw 的
   最後一個本文漢字「也」及其句末 `。`。
3. 10d_卷三上之一_0086-1
   segment.source 開頭是 `疏】…`：段標被截成半個（少了 `【`）。本段標籤
   已由網站依 segment.label 加上，source 不應再帶段標；去掉 `疏】`，讓
   source 從本文「一、」開始，與譯文一致。

安全條件
--------
- 三個 key 都只有 1 個 segment。
- 新 segment.source 的漢字必須是 row 漢字的連續子串；且新 source 必須
  等於該漢字子區間的「顯示切片」（前吃 opening、後吃 closing／句末）。
- 只改 segment.source；漢字僅去掉段標的「疏」，譯文不動。
- 寫檔前備份；只重寫受影響的 JSONL 行，其餘行 byte 不動。
- 寫檔後重驗：全書 source 漢字 == raw 區間、譯文 md5 不變、783 個
  「漢字序列定位不到」的 segment 數量不變。

用法
----
    python -X utf8 _src/fix_jieshu_segment_closeout.py          # dry-run
    python -X utf8 _src/fix_jieshu_segment_closeout.py --apply
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
OPEN = '「『【（《〔'
RIGHT = '」』】）》。！？，、；：》'

TARGETS = {
    '01c_卷一上之一_0059': ('title', '書名號／句末標點與 raw 邊界不符'),
    '戒疏-G19': ('tail_label', 'segment 尾多出下一單元的段標【疏】與開引號「'),
    '10d_卷三上之一_0086-1': ('head_label', 'segment 開頭段標截成半個「疏】」'),
}


def han(s):
    return ''.join(HAN.findall(s or ''))


def md5(s):
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()


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

    def disp_slice(self, a, b):
        l = self.pos[a]
        while l > 0 and self.text[l - 1] in OPEN:
            l -= 1
        r = self.pos[b - 1] + 1
        while r < len(self.text) and self.text[r] in RIGHT:
            r += 1
        return self.text[l:r]


def desired(kind, row_source):
    if kind == 'title':
        return row_source
    if kind == 'tail_label':
        # 去掉段末換行＋段標＋開引號
        s = re.sub(r'\n[\u3000 \t]*【[^】]+】[「『]?\s*$', '', row_source)
        return s
    if kind == 'head_label':
        # 去掉段首半個或完整的段標
        return re.sub(r'^(?:【[^】]+】|[疏記律註]】)', '', row_source)
    raise ValueError(kind)


def locate_seg(ch, body_han, a, b, cur):
    if not body_han:
        return None
    for lo in (cur, a, max(0, a - 8)):
        q = ch.find(body_han, lo)
        if q >= 0 and q + len(body_han) <= b:
            return q
    return None


def count_unlocatable(rows, corpus):
    """與 fix_jieshu_source_boundary.py 相同的 segment 定位規則。"""
    n = 0
    for r in rows:
        a, b = int(r.get('raw_start', -1) or -1), int(r.get('raw_end', -1) or -1)
        cur = a
        for s in r.get('segments') or []:
            body = re.sub(r'^(?:【[^】]+】)+', '', (s.get('source') or '').strip())
            bh = han(body)
            if not bh:
                continue
            q = locate_seg(corpus.ch, bh, a, b, cur)
            if q is None:
                n += 1
                continue
            cur = q + len(bh)
    return n


def build_plan():
    raw_lines = io.open(JSONL, encoding='utf-8').read().splitlines()
    rows = [json.loads(x) for x in raw_lines if x.strip()]
    corpus = Corpus(io.open(RAW, encoding='utf-8').read())
    by_key = {r.get('key'): r for r in rows}
    plan = []
    errors = []
    for key, (kind, why) in TARGETS.items():
        r = by_key.get(key)
        if r is None:
            errors.append((key, '找不到 row'))
            continue
        segs = r.get('segments') or []
        if len(segs) != 1:
            errors.append((key, '不是單一 segment', len(segs)))
            continue
        a, b = int(r['raw_start']), int(r['raw_end'])
        if corpus.disp_slice(a, b) != r.get('source'):
            errors.append((key, 'row.source != raw 顯示切片'))
            continue
        old = segs[0].get('source') or ''
        new = desired(kind, r['source'])
        # 新 source 必須是 row 漢字的連續子串，且等於該子區間的顯示切片
        rh = corpus.ch[a:b]
        nh = han(new)
        if not nh or nh not in rh:
            errors.append((key, '新 source 漢字不是 row 漢字的連續子串'))
            continue
        q = rh.find(nh)
        if corpus.disp_slice(a + q, a + q + len(nh)) != new:
            errors.append((key, '新 source != 該漢字子區間的顯示切片', repr(new[:20])))
            continue
        if not set(han(old)) - set(nh) <= set('疏'):
            errors.append((key, '舊 source 有非段標漢字被去掉'))
            continue
        if old == new:
            continue
        plan.append({
            'key': key, 'why': why, 'raw_start': a, 'raw_end': b,
            'old': old, 'new': new,
            'tr_md5': md5(segs[0].get('translation')),
        })
    return rows, raw_lines, corpus, plan, errors


def apply_plan(rows, raw_lines, plan):
    changes = {p['key']: p for p in plan}
    out = []
    touched = 0
    for line in raw_lines:
        if not line.strip():
            out.append(line)
            continue
        o = json.loads(line)
        p = changes.get(o.get('key'))
        if p is None:
            out.append(line)          # 未受影響的行 byte 不動
            continue
        assert md5(o['segments'][0].get('translation')) == p['tr_md5']
        o['segments'][0]['source'] = p['new']
        out.append(json.dumps(o, ensure_ascii=False))
        touched += 1
    assert touched == len(changes), (touched, len(changes))
    stamp = time.strftime('%Y%m%d_%H%M%S')
    bak = os.path.join(B, '定稿', '_舊_jieshu_before_segclose_%s.jsonl' % stamp)
    shutil.copy2(JSONL, bak)
    tmp = JSONL + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    os.replace(tmp, JSONL)
    return bak


def verify(corpus, before_rows, plan):
    rows = [json.loads(x) for x in io.open(JSONL, encoding='utf-8') if x.strip()]
    out = {'rows': len(rows), 'han_mismatch': 0, 'tr_changed': 0,
           'target_mismatch': 0, 'unlocatable': count_unlocatable(rows, corpus),
           'empty_seg_tr': 0}
    before = {r['key']: r for r in before_rows}
    for r in rows:
        a, b = int(r.get('raw_start', -1) or -1), int(r.get('raw_end', -1) or -1)
        if not (0 <= a < b <= len(corpus.ch)) or corpus.ch[a:b] != han(r.get('source')):
            out['han_mismatch'] += 1
        if md5(r.get('translation')) != md5(before[r['key']].get('translation')):
            out['tr_changed'] += 1
        for s in r.get('segments') or []:
            if not han(s.get('translation')):
                out['empty_seg_tr'] += 1
    for p in plan:
        r = next(x for x in rows if x['key'] == p['key'])
        if (r['segments'][0].get('source') or '') != p['new']:
            out['target_mismatch'] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    rows, raw_lines, corpus, plan, errors = build_plan()
    print('rows', len(rows), 'targets', len(TARGETS), 'changes', len(plan),
          'errors', len(errors))
    for e in errors:
        print('  ERR', e)
    for p in plan:
        print('  %s  %s' % (p['key'], p['why']))
        print('    old: %r' % p['old'][-60:])
        print('    new: %r' % p['new'][-60:])
    print('before unlocatable segments', count_unlocatable(rows, corpus))
    if errors:
        return 1
    if not args.apply:
        print('dry-run；加 --apply 才寫入')
        return 0
    bak = apply_plan(rows, raw_lines, plan)
    print('backup', bak)
    v = verify(corpus, rows, plan)
    print('VERIFY', v)
    ok = (v['han_mismatch'] == 0 and v['tr_changed'] == 0
          and v['target_mismatch'] == 0 and v['empty_seg_tr'] == 0
          and v['unlocatable'] == 783)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
