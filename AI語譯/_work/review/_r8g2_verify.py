import io, os, re, sys, csv
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/fix_r8_g2.tsv'
raw = io.open(p, 'rb').read()
print('bytes', len(raw), 'BOM', raw[:3] == b'\xef\xbb\xbf')
txt = raw.decode('utf-8')
print('ends with newline:', txt.endswith('\n'))
lines = txt.rstrip('\n').split('\n')
print('lines', len(lines))
keys = []
for i, ln in enumerate(lines, 1):
    f = ln.split('\t')
    assert len(f) == 4, (i, len(f))
    book, chunk, seg, new = f
    assert new.strip(), i
    assert '\r' not in ln
    keys.append((book, chunk, seg))

live = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in live:
        fp = os.path.join('AI語譯', 'out', book, chunk + '.txt')
        live[k] = [x for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
    return live[k]

print('rows', len(keys), 'unique', len(set(keys)))
bad = 0
for i, ln in enumerate(lines, 1):
    book, chunk, seg, new = ln.split('\t')
    base = paras(book, chunk)[int(seg) - 1]
    if base == new:
        print('NO-CHANGE row', i, book, chunk, seg); bad += 1
    # every new paragraph must start with the same first 6 chars as base (no re-header)
    if base[:6] != new[:6]:
        print('HEAD CHANGED row', i, book, chunk, seg, repr(base[:8]), repr(new[:8]))
print('bad', bad)

extra = io.open('AI語譯/_work/review/fix_r8_g2_extra.tsv', 'rb').read().decode('utf-8')
el = extra.rstrip('\n').split('\n')
print('extra lines', len(el))
for i, ln in enumerate(el, 1):
    f = ln.split('\t')
    assert len(f) == 4, (i, len(f))
    book, chunk, seg, new = f
    base = paras(book, chunk)[int(seg) - 1]
    assert base != new
    print('extra', book, chunk, seg, 'len', len(new))
