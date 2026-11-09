import csv, sys, io, collections
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/report_re7.tsv'
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
g = [(i, row) for i, row in rows if row['book'] == '03_業疏']
print('g2 rows:', len(g))
# stats: no suggestion, empty problem, already applied (problem text not in current)
nosug = sum(1 for _, row in g if not (row.get('suggestion') or '').strip())
print('no suggestion:', nosug)
# check duplicated (chunk, seg)
c = collections.Counter((row['chunk'], row['seg']) for _, row in g)
print('unique (chunk,seg):', len(c), 'multi:', sum(1 for k, v in c.items() if v > 1))
with open('AI語譯/_work/review/_g2r7_rows.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerow(['ridx'] + hdr)
    for i, row in g:
        w.writerow([i] + [row[h] for h in hdr])
