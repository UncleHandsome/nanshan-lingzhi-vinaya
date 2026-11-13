# -*- coding: utf-8 -*-
"""嚴格比對：只有校勘條目的上下文實際含「疑詞」才算命中。"""
import glob
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
IDX = os.path.join(B, '測試', '校勘索引.tsv')
SRC = os.path.join(B, '存疑材料', '待處理')
OUT = os.path.join(B, '測試', '待核_校勘比對.md')

# 這些是泛用詞，不作疑詞
STOP = {'原文', '譯文', '記文', '存疑', '疑點', '現譯', '依據', '判定', '建議',
        '不改', '仍存疑', '未改', '照錄', '兩讀', '皆通', '可疑', '待核'}


def load_index():
    rows = []
    for line in io.open(IDX, encoding='utf-8').read().split('\n')[1:]:
        if not line.strip():
            continue
        f = line.split('\t')
        if len(f) >= 6:
            rows.append(f)
    return rows


def terms_of(text):
    """抽疑詞：引號內 2–6 字，排除泛用詞。"""
    ts = set()
    for m in re.findall(r'[「『]([^」』]{2,6})[」』]', text):
        m = m.strip()
        if m and m not in STOP:
            ts.add(m)
    return ts


def main():
    idx = load_index()
    entries = []
    for p in sorted(glob.glob(os.path.join(SRC, '*.md'))):
        t = io.open(p, encoding='utf-8').read()
        cur = None
        for line in t.split('\n'):
            if re.match(r'^\s*(?:[-*]|\d+[.、])', line) and re.search(r'\d{3,4}-\d{3,4}', line):
                if cur:
                    entries.append(cur)
                cur = [line]
            elif cur is not None:
                cur.append(line)
        if cur:
            entries.append(cur)

    out = ['# 待核條目 × 校勘索引（嚴格比對）', '']
    hit = 0
    lines_hit = []
    for e in entries:
        text = ' '.join(e)
        ts = terms_of(text)
        if not ts:
            continue
        matched = []
        for book, loc, ctx, lem, rdg, wit in idx:
            # 條件：上下文含疑詞，且疑詞與正/異字有交集（表示該處確有異文涉及此詞）
            if any(k in ctx for k in ts):
                # 疑詞中的任一字＝正字或異文，才算「該詞確有異文」
                chars = set(lem) | set(rdg)
                if any(set(k) & chars for k in ts):
                    matched.append((book, loc, ctx, lem, rdg, wit))
        if matched:
            hit += 1
            lines_hit.append((re.sub(r'\*\*', '', e[0]).strip()[:90], matched[:4]))
    out.append('共 %d 條（總 %d 條）嚴格命中' % (hit, len(entries)))
    out.append('')
    for head, ms in lines_hit:
        out.append('### ' + head)
        for b, loc, ctx, lem, rdg, wit in ms:
            out.append('- `%s` %s：正「%s」／異「%s」（%s）｜…%s…' % (b, loc, lem, rdg, wit, ctx[:50]))
        out.append('')
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('總 %d 條，嚴格命中 %d → %s' % (len(entries), hit, OUT))


if __name__ == '__main__':
    main()