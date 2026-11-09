import csv, io, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'AI語譯'
rows = list(csv.DictReader(io.open('AI語譯/_work/review/_r8g2_rows.tsv', encoding='utf-8', newline=''), delimiter='\t'))
cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = os.path.join(BASE, 'out', book, chunk + '.txt')
        txt = io.open(p, encoding='utf-8').read()
        cache[k] = [x for x in re.split(r'\r?\n\r?\n', txt) if x.strip()]
    return cache[k]
ok = 0
for r in rows:
    ps = paras(r['book'], r['chunk'])
    i = int(r['seg']) - 1
    p = ps[i] if 0 <= i < len(ps) else '<OOR>'
    same = (p == r['current'])
    ok += same
    print('%s %s/%s#%s  paras=%d  match=%s  curlen=%d outlen=%d' % (
        r['ridx'], r['book'], r['chunk'], r['seg'], len(ps), same, len(r['current']), len(p)))
print('match', ok, '/', len(rows))
