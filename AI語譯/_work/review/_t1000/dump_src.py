# -*- coding: utf-8 -*-
"""Dump source paragraphs for chosen (book, chunk, seg)."""
import io, os, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
targets = [
    ('01_行事鈔', '00_卷首', [6, 8, 54]),
    ('01_行事鈔', '01a_卷上之一', [24, 28, 29, 30]),
    ('01_行事鈔', '01b_卷上之一', [39, 59, 63, 77]),
    ('01_行事鈔', '07b_卷中之三', [29, 30, 32, 35]),
    ('01_行事鈔', '07d_卷中之三', [4]),
]
out = []
for book, chunk, segs in targets:
    sp = os.path.join(B, 'TXT_分卷', book, chunk + '.txt')
    op = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    src = [x for x in io.open(sp, encoding='utf-8-sig').read().split('\n\n') if x.strip()]
    dst = [x for x in io.open(op, encoding='utf-8-sig').read().split('\n\n') if x.strip()]
    out.append('#' * 90)
    out.append('%s/%s  src=%d out=%d' % (book, chunk, len(src), len(dst)))
    for s in segs:
        out.append('--- seg %d ---' % s)
        out.append('[原文] ' + (src[s-1] if s <= len(src) else 'NA'))
        out.append('[譯文] ' + (dst[s-1] if s <= len(dst) else 'NA'))
        out.append('')
io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'src.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
