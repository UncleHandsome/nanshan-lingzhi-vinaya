import csv, json, sys, os
p = r'AI語譯/_work/review/report_re4.tsv'
with open(p, encoding='utf-8') as f:
    rows = list(csv.reader(f, delimiter='\t'))
hdr = rows[0]
books = {'資持記', '03_業疏', '01_行事鈔'}
sel = [r for r in rows[1:] if r[1] in books]
out = []
for i, r in enumerate(sel):
    d = dict(zip(hdr, r))
    d['_n'] = i
    out.append(d)
json.dump(out, open(r'AI語譯/_work/review/_re4g2_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('selected', len(out))
print('no-suggestion', sum(1 for d in out if not d['suggestion'].strip()))
from collections import Counter
print(Counter(d['book'] for d in out))
print(Counter(d['level'] for d in out))
print(Counter(d['cls'] for d in out))
