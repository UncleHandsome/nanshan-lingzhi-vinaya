# -*- coding: utf-8 -*-
"""套用 Qwen parts 回覆：白話與 canonical segments 一起切。

回覆格式：
  {"book_id":"...","key":"...","parts":[
    {"segment":1,"from":1,"to":2,"translation":"..."},
    {"segment":1,"from":3,"to":4,"translation":"..."}
  ]}

用法：
  python -X utf8 _src/apply_parts.py --reply 六書_500字_長段優先/AI輸出 --dry-run
  python -X utf8 _src/apply_parts.py --reply ... --apply
"""
import argparse
import glob
import io
import json
import os
import shutil

import make_500_longfirst as M

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def load_rows(book):
    p = os.path.join(B, '定稿', book + '.jsonl')
    return [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]


def parse_parts(o):
    parts = o.get('parts') or []
    if not parts:
        return None, 'no parts'
    out = []
    for p in parts:
        try:
            seg = int(p['segment'])
        except Exception:
            return None, 'bad segment'
        head = str(p.get('head') or '').strip()
        tr = str(p.get('translation') or '').strip()
        if seg < 1 or not head or not tr:
            return None, 'bad part'
        out.append((seg, head, tr))
    return out, ''


def split_row(row, parts):
    segs = row.get('segments') or []
    if not segs:
        return None, 'no canonical segments'
    by = {}
    for seg, head, tr in parts:
        by.setdefault(seg, []).append((head, tr))
    if sorted(by) != list(range(1, len(segs) + 1)):
        return None, 'segment numbers mismatch'
    new_segs = []
    full_tr = []
    for i, seg in enumerate(segs, 1):
        ss = (seg.get('display_source') or seg.get('source') or '').strip()
        if not ss:
            return None, 'empty segment'
        ps = by[i]
        pos = []
        for j, (head, tr) in enumerate(ps):
            idx = ss.find(head)
            if idx < 0:
                return None, 'head not found: ' + head[:20]
            if ss.find(head, idx + 1) >= 0:
                return None, 'head not unique: ' + head[:20]
            if j == 0 and idx != 0:
                return None, 'first head not at start'
            if pos and idx <= pos[-1]:
                return None, 'head order'
            pos.append(idx)
        for j, (head, tr) in enumerate(ps):
            a = pos[j]; b = pos[j + 1] if j + 1 < len(ps) else len(ss)
            src = ss[a:b]
            s2 = dict(seg)
            s2['source'] = src
            s2['display_source'] = src
            s2['translation'] = tr
            new_segs.append(s2)
            full_tr.append(tr)
    return new_segs, full_tr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reply', required=True)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    replies = []
    for p in glob.glob(os.path.join(args.reply, '**', '*_回.txt'), recursive=True) + glob.glob(os.path.join(args.reply, '**', '*_修正.jsonl'), recursive=True):
        for ln in io.open(p, encoding='utf-8'):
            ln = ln.strip()
            if not ln or ln.upper().rstrip('.。') == 'NONE':
                continue
            replies.append(json.loads(ln))
    changed = {}; ok = bad = 0
    for o in replies:
        book = o.get('book_id'); key = str(o.get('key') or '')
        if '／' in key: key = key.rsplit('／', 1)[-1]
        elif '/' in key: key = key.rsplit('/', 1)[-1]
        o['key'] = key
        parts, err = parse_parts(o)
        if not book or not key or not parts:
            print('SKIP', book, key, err); bad += 1; continue
        rows = load_rows(book); by = {str(r['key']): r for r in rows}
        r = by.get(key)
        if not r:
            print('SKIP missing', book, key); bad += 1; continue
        new_segs, info = split_row(r, parts)
        if not new_segs:
            print('SKIP', book, key, info); bad += 1; continue
        print('OK', book, key, 'old_segs', len(r.get('segments') or []), 'new_segs', len(new_segs))
        ok += 1
        if not args.apply:
            continue
        r['translation'] = '\n\n'.join(info)
        r['segments'] = new_segs
        changed[(book, key)] = (new_segs, info)
    if args.apply and changed:
        for book in {b for b, _ in changed}:
            p = os.path.join(B, '定稿', book + '.jsonl')
            shutil.copy2(p, os.path.join(B, '定稿', '_舊_%s_before_parts_20261124.jsonl' % book))
            rows = load_rows(book)
            by = {str(r['key']): r for r in rows}
            for (b, k), (segs, trs) in changed.items():
                if b != book or k not in by: continue
                by[k]['translation'] = '\n\n'.join(trs)
                by[k]['segments'] = segs
            io.open(p, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    print('ok', ok, 'bad', bad)


if __name__ == '__main__':
    main()
