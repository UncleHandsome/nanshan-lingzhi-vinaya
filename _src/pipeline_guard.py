# -*- coding: utf-8 -*-
"""五書頁面／終審材料的最低防線。

用法：
    python -X utf8 _src/pipeline_guard.py
    python -X utf8 _src/pipeline_guard.py --book nicao
"""
import argparse
import io
import os
import re
import sys
import html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
    'xingshichao': ('行事鈔', ('卷上', '卷中', '卷下'), 'TXT/01_四分律刪繁補闕行事鈔.txt'),
    'jieshu': ('戒疏', ('卷一', '卷二', '卷三', '卷四'), 'TXT/02_四分律含注戒本疏.txt'),
    'yeshu': ('業疏', ('卷一', '卷二', '卷三', '卷四'), 'TXT/03_四分律刪補隨機羯磨疏.txt'),
    'nicao': ('尼鈔', ('卷上', '卷中', '卷下'), 'TXT/04_四分律比丘尼鈔.txt'),
    'yichao': ('義鈔', ('卷上', '卷中'), 'TXT/05_四分律拾毗尼義鈔.txt'),
}


def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', s.strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def check(book):
    name, vols, rawp = BOOKS[book]
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    for c in raw:
        if re.match(r'[\u4e00-\u9fff]', c):
            h += c
    recs = []
    errors = []
    short = 0
    for v in vols:
        p = os.path.join(B, 'docs', book, v + '.html')
        t = io.open(p, encoding='utf-8').read()
        if '&lt;br' in t:
            errors.append('%s 有 &lt;br&gt; 殘留' % v)
        for m in re.finditer(r'<div class="pair[^"]*"[^>]*><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
            o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))
            tr = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
            if not tr.strip():
                errors.append('%s 有空白白話' % v)
            if '白話：' in tr:
                errors.append('%s 白話殘留「白話：」' % v)
            for bad in ('【後文背景', '【裁決', '【分段要求', '【必改硬傷】', '【卷題】'):
                if bad in o or bad in tr:
                    errors.append('%s 殘留 %s' % (v, bad))
                    break
            s = han(o)
            if not s:
                continue
            if len(s) <= 2:
                short += 1
            q = h.find(s[:20])
            if q < 0:
                q = h.find(s[:12])
            if q < 0:
                q = h.find(s[:8])
            if q < 0:
                errors.append('%s 對不到 raw：%s' % (v, s[:20]))
                continue
            recs.append((q, q + len(s)))
    cover = [0] * len(h)
    for a, b in recs:
        for i in range(a, min(b, len(h))):
            cover[i] += 1
    gaps = 0
    i = 0
    while i < len(h):
        if cover[i] == 0:
            j = i
            while j < len(h) and cover[j] == 0:
                j += 1
            if j - i >= 20:
                gaps += 1
            i = j
        else:
            i += 1
    dups = sum(1 for a, b in recs if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
    print('%s：pairs=%d gaps=%d overlaps=%d short<=2=%d errors=%d' % (name, len(recs), gaps, dups, short, len(errors)))
    for e in errors[:10]:
        print('  -', e)
    return errors, gaps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', choices=sorted(BOOKS))
    args = ap.parse_args()
    books = [args.book] if args.book else list(BOOKS)
    bad = 0
    for b in books:
        errs, gaps = check(b)
        if errs or gaps:
            bad += 1
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
