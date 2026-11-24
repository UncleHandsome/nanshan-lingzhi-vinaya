# -*- coding: utf-8 -*-
"""補回 display_source 尾端標點：以 source 尾端標點為準（content-neutral）。

只處理 han(source)==han(display_source) 的段：
source 尾端有標點（如 。；：，」）、display 卻沒有者，把該標點串補到 display 尾端。
不動 source／translation／key／raw_start。

用法：
  python -X utf8 _src/fix_display_tail_punct.py            # dry-run
  python -X utf8 _src/fix_display_tail_punct.py --apply
  python -X utf8 _src/fix_display_tail_punct.py --apply zhichi nicao
"""
import io
import json
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff]')
PUN = set('。！？；：，、」』）】…·')
BOOKS = ['xingshichao', 'jieshu', 'yeshu', 'nicao', 'yichao', 'zhichi']


def han(s):
    return ''.join(HAN.findall(s or ''))


def tail_run(s):
    s = (s or '').rstrip()
    i = len(s)
    while i > 0 and s[i - 1] in PUN:
        i -= 1
    return s[i:]


def fix_tail(disp, src):
    if not disp or not src:
        return disp
    if han(disp) != han(src):
        return disp
    d = disp.rstrip()
    if d and d[-1] in PUN:
        return disp
    tail = tail_run(src)
    if not tail:
        return disp
    return d + tail


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    apply = '--apply' in sys.argv
    books = [b for b in args if b in BOOKS] or BOOKS
    for book in books:
        path = os.path.join(B, '定稿', book + '.jsonl')
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        n = 0
        for r in rows:
            segs = r.get('segments') or []
            if not segs:
                nd = fix_tail(r.get('display_source') or '', r.get('source') or '')
                if nd != (r.get('display_source') or ''):
                    r['display_source'] = nd
                    n += 1
                continue
            for s in segs:
                nd = fix_tail(s.get('display_source') or '', s.get('source') or '')
                if nd != (s.get('display_source') or ''):
                    s['display_source'] = nd
                    n += 1
            nd = fix_tail(r.get('display_source') or '', r.get('source') or '')
            if nd != (r.get('display_source') or ''):
                r['display_source'] = nd
                n += 1
            # 若 row 尾端有標點、最後一段卻沒有，補到最後一段
            rd = r.get('display_source') or ''
            sd = segs[-1].get('display_source') or ''
            if (rd and sd and han(rd) == han(r.get('source') or '')
                    and han(sd) == han(segs[-1].get('source') or '')):
                tail = tail_run(rd)
                if tail and not sd.rstrip().endswith(tuple(PUN)):
                    segs[-1]['display_source'] = sd.rstrip() + tail
                    n += 1
        print(book, 'fixed', n, flush=True)
        if apply and n:
            bak = path + '.bak_tailpunct_20261124'
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    if not apply:
        print('dry-run; add --apply')


if __name__ == '__main__':
    main()
