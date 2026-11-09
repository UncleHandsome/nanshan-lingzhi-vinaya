# -*- coding: utf-8 -*-
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

p = r'AI語譯/_work/review/fix_r8b_g2.tsv'
raw = io.open(p, 'rb').read()
print('bytes', len(raw), 'BOM', raw[:3] == b'\xef\xbb\xbf')
txt = raw.decode('utf-8')
print('ends with newline:', txt.endswith('\n'))
lines = txt.rstrip('\n').split('\n')
print('lines', len(lines))

keys = []
paras = {}
def para(book, chunk, seg):
    k = (book, chunk)
    if k not in paras:
        fp = os.path.join('AI語譯', 'out', book, chunk + '.txt')
        paras[k] = [x for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
    return paras[k][int(seg) - 1]

for i, ln in enumerate(lines, 1):
    f = ln.split('\t')
    assert len(f) == 4, (i, len(f))
    book, chunk, seg, new = f
    assert new.strip() and '\r' not in ln and '\n' not in new
    keys.append((book, chunk, seg))
    base = para(book, chunk, seg)
    assert base != new, ('no change', i)
    # length sanity
    print('%2d %s %s#%s  %d->%d' % (i, book, chunk, seg, len(base), len(new)))
print('rows', len(keys), 'unique', len(set(keys)))
books = set(k[0] for k in keys)
print('books', books)
