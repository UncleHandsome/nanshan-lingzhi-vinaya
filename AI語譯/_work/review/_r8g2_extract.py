import csv, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/report_r8.tsv'
rows = []
with open(p, encoding='utf-8', newline='') as f:
    r = csv.DictReader(f, delimiter='\t')
    hdr = r.fieldnames
    for i, row in enumerate(r):
        rows.append((i, row))
print('header:', hdr)
print('total rows:', len(rows))
cnt = collections.Counter(row['book'] for _, row in rows)
print('books:', cnt)
books = ('02_戒疏', '資持記', '01_行事鈔')
g = [(i, row) for i, row in rows if row['book'] in books]
print('target rows:', len(g))
c2 = collections.Counter(row['book'] for _, row in g)
print('target books:', c2)
nosug = sum(1 for _, row in g if not (row.get('suggestion') or '').strip())
print('no suggestion:', nosug)
c = collections.Counter((row['book'], row['chunk'], row['seg']) for _, row in g)
print('unique (book,chunk,seg):', len(c), 'multi:', sum(1 for k, v in c.items() if v > 1))
with open('AI語譯/_work/review/_r8g2_rows.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['ridx'] + hdr)
    for i, row in g:
        w.writerow([i] + [row[h] for h in hdr])
