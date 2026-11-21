# -*- coding: utf-8 -*-
"""由定稿 JSONL 輸出 docs/<book>/<vol>.new。先不覆蓋。"""
import argparse
import io
import json
import os
import re
import html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
BOOKS = {
    'xingshichao': ('行事鈔', ('卷上', '卷中', '卷下')),
    'jieshu': ('戒疏', ('卷一', '卷二', '卷三', '卷四')),
    'yeshu': ('業疏', ('卷一', '卷二', '卷三', '卷四')),
    'nicao': ('尼鈔', ('卷上', '卷中', '卷下')),
    'yichao': ('義鈔', ('卷上', '卷中')),
}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')


def split_labels(text):
    text = (text or '').strip()
    ms = list(re.finditer(r'【([^】]+)】', text))
    ms = [m for m in ms if m.group(1) in LABELS]
    if not ms:
        return []
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end].strip()
        if body:
            out.append((m.group(1), body))
    return out


def pairs_for(row):
    segs = row.get('segments') or []
    if segs:
        return [(s.get('label') or '疏文', s.get('source', ''), s.get('translation', '')) for s in segs]
    label = row.get('label') or '疏文'
    return [(label, row.get('source', '').strip(), row.get('translation', '').strip())]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', choices=sorted(BOOKS))
    args = ap.parse_args()
    books = [args.book] if args.book else list(BOOKS)
    for book in books:
        name, vols = BOOKS[book]
        rows = [json.loads(x) for x in io.open(os.path.join(C, book + '.jsonl'), encoding='utf-8') if x.strip()]
        rows.sort(key=lambda r: (r.get('raw_start', 10**9) if r.get('raw_start', -1) >= 0 else 10**9, r.get('key', '')))
        total = 0
        for v in vols:
            sel = [r for r in rows if r.get('vol') == v]
            if not sel:
                continue
            body = ['<h1>%s・%s</h1>' % (name, v), '<p class="byline">%d 單元；原文與白話逐段並列。</p>' % len(sel)]
            last = None
            idx = 0
            for r in sel:
                chunk = r.get('chunk') or v
                if chunk != last:
                    idx += 1
                    body.append('<h2 class="sec" id="p%d">%s</h2>' % (idx, html.escape(chunk)))
                    last = chunk
                for lab, s, tr in pairs_for(r):
                    if not s or not tr:
                        continue
                    body.append('<div class="pair"><div class="o">【%s】%s</div><div class="t">【%s】%s</div></div>' % (
                        lab, html.escape(s).replace('\n', '<br>'), lab, html.escape(tr).replace('\n', '<br>')))
                    total += 1
            p = os.path.join(B, 'docs', book, v + '.html')
            t = io.open(p, encoding='utf-8').read()
            m = re.search(r'<main id="main">.*?</main>', t, re.S)
            new = t[:m.start()] + '<main id="main">' + ''.join(body) + '</main>' + t[m.end():]
            io.open(p + '.new', 'w', encoding='utf-8').write(new)
            print('%s %s -> %s' % (name, v, p + '.new'))
        print(name, 'pairs', total)


if __name__ == '__main__':
    main()
