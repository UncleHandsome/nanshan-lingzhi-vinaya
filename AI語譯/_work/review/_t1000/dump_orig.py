# -*- coding: utf-8 -*-
"""Index 校閱_單段 files by (book, chunk, seg) from first line, then dump 原文 for entries."""
import io, os, json, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '校閱_單段')
idx = {}
for p in glob.glob(os.path.join(D, '*.txt')):
    with io.open(p, encoding='utf-8-sig') as f:
        head = f.readline().strip()
    m = re.match(r'^【(.+?)/(.+?)#(\d+)】$', head)
    if m:
        idx[(m.group(1), m.group(2), int(m.group(3)))] = p
print('indexed', len(idx))

d = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'entries.json'), encoding='utf-8'))
out = []
miss = []
for k, e in enumerate(d['uniq'], 1):
    p = idx.get((e['book'], e['chunk'], e['seg']))
    out.append('=' * 100)
    out.append('[%02d] %s | %s | %s' % (k, e['gid'], e['level'], e['cat']))
    out.append('問題：' + e['problem'])
    out.append('建議：' + e['suggestion'])
    if not p:
        out.append('(missing snapshot)')
        miss.append(e['gid'])
        continue
    t = io.open(p, encoding='utf-8-sig').read()
    orig = re.search(r'【原文】(.*?)(?:\n【|$)', t, re.S)
    out.append('原文：' + (orig.group(1).strip() if orig else ''))
    out.append('file：' + os.path.basename(p))
io.open(os.path.join(B, 'AI語譯', '_work', 'review', '_t1000', 'orig2.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('missing', miss)
