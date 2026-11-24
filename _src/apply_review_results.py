# -*- coding: utf-8 -*-
"""套用 review_entries 產出的「輸入與結果」檔：解析 JSONL，把 status=fixed 的
translation 寫回定稿對應 segment。

用法：
  python -X utf8 _src/apply_review_results.py --dir 抽樣_新段落_20261124 --dry-run
  python -X utf8 _src/apply_review_results.py --dir 抽樣_新段落_20261124 --apply
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import run_3k_review as R

B = R.B
JSONL_BLK = re.compile(r'<<<JSONL_START>>>(.*?)<<<JSONL_END>>>', re.S)
SEC = re.compile(r'^##\s+([^／\n]+)／(\S+)\s*$', re.M)


def parse_result(path):
    """回傳 (expected_mks, rows)；rows 為 [dict(...)]。"""
    t = io.open(path, encoding='utf-8').read()
    # 輸入區段：## 書／key
    i = t.find('## 輸入')
    j = t.find('## 千問結果', i)
    entry = t[i:j] if i >= 0 and j > i else t
    expected = [k for _, k in SEC.findall(entry)]
    books = [n for n, _ in SEC.findall(entry)]
    blocks = JSONL_BLK.findall(t)
    rows = []
    if blocks:
        for ln in blocks[-1].strip().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except Exception:
                pass
    return expected, books, rows


def strip_label(tr, label):
    """若舊譯沒有【label】前綴，把新譯的【label】\n 去掉，維持段落格式。"""
    m = re.match(r'^【([^】]{1,4})】\s*\n?', tr)
    if m and m.group(1) == label:
        return tr[m.end():].lstrip()
    return tr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir')
    ap.add_argument('--files', nargs='*')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    files = list(a.files or [])
    if a.dir:
        files += sorted(glob.glob(os.path.join(a.dir, '*輸入與結果.md')))
    keymap = R.all_segment_keys()
    fixes = []
    for p in files:
        expected, books, rows = parse_result(p)
        book = None
        for n in books:
            for bid, prof in __import__('book_prompt').PROFILES.items():
                if n.strip() == prof['name']:
                    book = bid
                    break
            if book:
                break
        for o in rows:
            if str(o.get('status')) != 'fixed':
                continue
            tr = (o.get('translation') or '').strip()
            if not tr:
                continue
            mk = R.match_key(o.get('key'), expected)
            kid = '%s|%s' % (book, mk) if book else None
            if not kid or kid not in keymap:
                print('SKIP unmatched', os.path.basename(p), o.get('key'), '->', mk)
                continue
            book, rowkey, si, lab, seg = keymap[kid]
            old = seg.get('translation') or ''
            new = tr if re.match(r'^【', old) else strip_label(tr, seg.get('label') or lab or '鈔文')
            if new == old:
                print('SAME', mk)
                continue
            fixes.append((book, rowkey, si, mk, old, new))
            print('FIX', mk, 'old_len', len(old), 'new_len', len(new))
    print('total fixes', len(fixes))
    if not a.apply or not fixes:
        return
    bybook = {}
    for f in fixes:
        bybook.setdefault(f[0], []).append(f)
    for book, fs in bybook.items():
        path = os.path.join(B, '定稿', book + '.jsonl')
        bak = os.path.join(B, '定稿', '_舊_%s_before_review_apply_%s.jsonl'
                           % (book, time.strftime('%Y%m%d_%H%M%S')))
        shutil.copy2(path, bak)
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        bykey = {str(r['key']): r for r in rows}
        n = 0
        for _, rowkey, si, mk, old, new in fs:
            r = bykey.get(rowkey)
            if not r:
                continue
            segs = r.get('segments') or []
            if 1 <= si <= len(segs):
                segs[si - 1]['translation'] = new
                r['translation'] = '\n\n'.join((s.get('translation') or '') for s in segs)
                n += 1
        io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
            json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
        print('applied', book, n, 'backup', os.path.basename(bak))


if __name__ == '__main__':
    main()
