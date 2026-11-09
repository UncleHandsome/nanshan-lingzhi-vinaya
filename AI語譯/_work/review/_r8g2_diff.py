import csv, io, sys, os, re, difflib
sys.stdout.reconfigure(encoding='utf-8')
rows = list(csv.DictReader(io.open('AI語譯/_work/review/_r8g2_rows.tsv', encoding='utf-8', newline=''), delimiter='\t'))
cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = os.path.join('AI語譯', 'out', book, chunk + '.txt')
        cache[k] = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    return cache[k]
for r in rows:
    ps = paras(r['book'], r['chunk'])
    p = ps[int(r['seg']) - 1]
    if p == r['current']:
        continue
    print('=' * 90)
    print('RIDX %s %s/%s#%s  %s' % (r['ridx'], r['book'], r['chunk'], r['seg'], r['cls']))
    print('SUG:', r['suggestion'])
    sm = difflib.SequenceMatcher(None, r['current'], p, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        print('  %-8s report[...] = %r' % (tag, r['current'][max(0, i1 - 12):i2 + 12]))
        print('           out   [...] = %r' % (p[max(0, j1 - 12):j2 + 12]))
