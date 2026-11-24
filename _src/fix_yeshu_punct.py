# -*- coding: utf-8 -*-
"""修復 yeshu display_source 標點。

兩類問題：
 A. 段 display 整段無標點、source 有標點 → display 直接用 source（han 相同）。
 B. 段尾缺標點（source 尾有、display 尾無）→ 補 source 尾標點。
最後 row.display_source = 各段 display 串接。
"""
import io
import json
import os
import re
import shutil
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff]')
PUN = re.compile(r'[，。；：！？、]')
ENDS = set('。！？；：，、」』）】…')


def han(s):
    return ''.join(HAN.findall(s or ''))


def tail_run(s):
    s = (s or '').rstrip()
    i = len(s)
    while i > 0 and s[i - 1] in ENDS:
        i -= 1
    return s[i:]


def fix_one(disp, src):
    if not disp or not src or han(disp) != han(src):
        return disp
    if not PUN.search(disp) and PUN.search(src):
        return src.strip()
    d = disp.rstrip()
    if d and d[-1] in ENDS:
        return disp
    t = tail_run(src)
    return (d + t) if t else disp


def main():
    apply = '--apply' in sys.argv
    path = os.path.join(B, '定稿', 'yeshu.jsonl')
    rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
    n = 0
    for r in rows:
        segs = r.get('segments') or []
        if not segs:
            nd = fix_one(r.get('display_source') or '', r.get('source') or '')
            if nd != (r.get('display_source') or ''):
                r['display_source'] = nd
                n += 1
            continue
        for s in segs:
            nd = fix_one(s.get('display_source') or '', s.get('source') or '')
            if nd != (s.get('display_source') or ''):
                s['display_source'] = nd
                n += 1
        nd = fix_one(r.get('display_source') or '', r.get('source') or '')
        if nd != (r.get('display_source') or ''):
            r['display_source'] = nd
            n += 1
        # 尾段對齊 row 尾標點
        rd = r.get('display_source') or ''
        sd = segs[-1].get('display_source') or ''
        if (rd and sd and han(rd) == han(r.get('source') or '')
                and han(sd) == han(segs[-1].get('source') or '')):
            t_ = tail_run(rd)
            if t_ and not sd.rstrip().endswith(tuple(ENDS)):
                segs[-1]['display_source'] = sd.rstrip() + t_
                n += 1
    print('yeshu fixed', n)
    if apply:
        bak = path + '.bak_yeshu_punct_20261124'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
            json.dumps(x, ensure_ascii=False) + '\n' for x in rows)


if __name__ == '__main__':
    main()
