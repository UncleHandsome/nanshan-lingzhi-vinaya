# -*- coding: utf-8 -*-
import io, csv
from collections import Counter
for fn in ('fix_re3_g2.tsv', 'fix_re2_g2.tsv', 'fix_re4.tsv'):
    p = 'AI語譯/_work/review/' + fn
    try:
        rows = list(csv.reader(io.open(p, encoding='utf-8'), delimiter='\t'))
    except FileNotFoundError:
        print(fn, 'MISSING'); continue
    keys = Counter((r[0], r[1], r[2]) for r in rows)
    d = sum(1 for v in keys.values() if v > 1)
    print(fn, 'rows', len(rows), 'cols', len(rows[0]), 'dups', d, 'sample', rows[0][:3])
