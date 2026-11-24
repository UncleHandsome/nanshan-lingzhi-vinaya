# -*- coding: utf-8 -*-
"""六書定稿重新順序對齊原文：以 TXT 底本漢字序列（只计 4e00-9fff，與渲染器一致）
重算 raw_start／raw_end，依原文順序排序。不改 source／translation／segments。

用法：
  python -X utf8 _src/realign_raw.py            # 預覽
  python -X utf8 _src/realign_raw.py --apply
"""
import argparse
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HAN = re.compile(r'[\u4e00-\u9fff]')
RAWS = {
    'xingshichao': r'TXT\01_四分律刪繁補闕行事鈔.txt',
    'jieshu': r'TXT\02_四分律含注戒本疏.txt',
    'yeshu': r'TXT\03_四分律刪補隨機羯磨疏.txt',
    'nicao': r'TXT\04_四分律比丘尼鈔.txt',
    'yichao': r'TXT\05_四分律拾毗尼義鈔.txt',
}


def han(s):
    return ''.join(HAN.findall(s or ''))


def nearest(rh, t, anchor):
    """找 t 的所有出現，取最接近 anchor 的。"""
    best = None
    start = 0
    while True:
        p = rh.find(t, start)
        if p < 0:
            break
        if best is None or abs(p - anchor) < abs(best - anchor):
            best = p
        start = p + 1
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    report = {}
    for book, rf in RAWS.items():
        rh = han(io.open(os.path.join(B, rf), encoding='utf-8').read())
        path = os.path.join(B, '定稿', book + '.jsonl')
        rows = [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]
        kept = fixed = span = fail = 0
        issues = []
        cursor = 0
        for r in rows:
            t = han(r.get('source'))
            rs, re_ = r.get('raw_start'), r.get('raw_end')
            if not t:
                fail += 1
                issues.append((r['key'], 'empty'))
                continue
            if rs is not None and rh[rs:re_] == t:
                kept += 1
                cursor = max(cursor, re_)
                continue
            p = rh.find(t, cursor)
            if p < 0:
                p = nearest(rh, t, rs if rs is not None else cursor)
            if p is not None and p >= 0:
                r['raw_start'] = p
                r['raw_end'] = p + len(t)
                cursor = max(cursor, r['raw_end'])
                fixed += 1
                continue
            # 合併列：用首尾錨點取涵蓋區間（source 非連續，只對齊位置）
            pre, suf = t[:10], t[-10:]
            pp = nearest(rh, pre, rs if rs is not None else cursor)
            if pp is not None:
                qq = rh.find(suf, pp + len(pre))
                if qq >= 0:
                    r['raw_start'] = pp
                    r['raw_end'] = qq + len(suf)
                    cursor = max(cursor, r['raw_end'])
                    span += 1
                    issues.append((r['key'], 'span'))
                    continue
            fail += 1
            issues.append((r['key'], 'fail'))
        rows.sort(key=lambda r: (r.get('raw_start', 10 ** 9), r.get('raw_end', 10 ** 9), str(r.get('key'))))
        mono = all(rows[i].get('raw_start', 0) <= rows[i + 1].get('raw_start', 0) for i in range(len(rows) - 1))
        ok = sum(1 for r in rows if rh[r.get('raw_start'):r.get('raw_end')] == han(r.get('source')))
        report[book] = {'rows': len(rows), 'kept': kept, 'fixed': fixed, 'span': span,
                        'fail': fail, 'slice_ok': ok, 'monotonic': mono, 'issues': issues}
        print(book, 'kept', kept, 'fixed', fixed, 'span', span, 'fail', fail,
              'slice_ok', ok, 'mono', mono, flush=True)
        for k, why in issues:
            if why == 'fail':
                print('  FAIL', k, flush=True)
        if a.apply:
            shutil.copy2(path, os.path.join(B, '定稿', '_舊_%s_before_realign_20261124.jsonl' % book))
            io.open(path, 'w', encoding='utf-8', newline='\n').writelines(
                json.dumps(x, ensure_ascii=False) + '\n' for x in rows)
    # zhichi：座標系自成一套，只驗證順序
    zp = os.path.join(B, '定稿', 'zhichi.jsonl')
    zrows = [json.loads(x) for x in io.open(zp, encoding='utf-8') if x.strip()]
    zmono = all(zrows[i].get('raw_start', 0) <= zrows[i + 1].get('raw_start', 0) for i in range(len(zrows) - 1))
    report['zhichi'] = {'rows': len(zrows), 'monotonic': zmono, 'note': '座標系與 TXT 不同，僅驗證順序'}
    print('zhichi rows', len(zrows), 'mono', zmono, flush=True)
    io.open(os.path.join(B, '重作材料_長段', 'realign_report_20261124.json'), 'w',
            encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
