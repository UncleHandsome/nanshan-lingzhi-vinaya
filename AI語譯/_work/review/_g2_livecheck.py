# -*- coding: utf-8 -*-
import json, io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = json.loads(io.open(r'AI語譯\_work\review\_g2_rows.json', encoding='utf-8').read())
CACHE = {}

def paras(book, chunk):
    k = (book, chunk)
    if k not in CACHE:
        p = os.path.join('AI語譯', 'out', book, chunk + '.txt')
        CACHE[k] = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    return CACHE[k]

lines = []
for i, r in enumerate(rows):
    book, chunk, seg = r['book'], r['chunk'], int(r['seg'])
    try:
        base = paras(book, chunk)[seg - 1]
    except Exception as e:
        lines.append('[%d] %s %s#%s ERROR %s' % (i + 1, book, chunk, seg, e))
        continue
    same = (base == r['current'])
    lines.append('[%d] %s %s#%s same=%s liveLen=%d curLen=%d' % (i + 1, book, chunk, seg, same, len(base), len(r['current'])))
    if not same:
        # first difference
        n = min(len(base), len(r['current']))
        j = 0
        while j < n and base[j] == r['current'][j]:
            j += 1
        lines.append('    live: ...%s...' % base[max(0, j - 20):j + 40].replace('\n', ' '))
        lines.append('    cur : ...%s...' % r['current'][max(0, j - 20):j + 40].replace('\n', ' '))
io.open(r'AI語譯\_work\review\_g2_livecheck.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done', len(rows))
