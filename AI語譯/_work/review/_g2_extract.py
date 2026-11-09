# -*- coding: utf-8 -*-
import csv, io, json
from collections import Counter

p = r'AI語譯\_work\review\report_r8b.tsv'
rows = list(csv.reader(io.open(p, encoding='utf-8'), delimiter='\t'))[1:]
targets = {'資持記', '02_戒疏', '01_行事鈔'}
out = []
for i, r in enumerate(rows):
    if r[1] in targets:
        out.append({'line': i + 2, 'gid': r[0], 'book': r[1], 'chunk': r[2], 'seg': r[3],
                    'level': r[4], 'cls': r[5], 'problem': r[6], 'suggestion': r[7],
                    'orig': r[8], 'current': r[9]})
io.open(r'AI語譯\_work\review\_g2_rows.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))

lines = []
lines.append('count=%d groups=%d' % (len(out), len(set((r['book'], r['chunk'], r['seg']) for r in out))))
c = Counter((r['book'], r['chunk'], r['seg']) for r in out)
lines.append('multi: ' + repr([(k, v) for k, v in c.items() if v > 1]))
for r in out:
    lines.append('%s\t%s\t%s\tlen=%d\tno_sugg=%s' % (r['line'], r['gid'], r['seg'], len(r['current']), 'Y' if not r['suggestion'].strip() else ''))
io.open(r'AI語譯\_work\review\_g2_summary.txt', 'w', encoding='utf-8').write('\n'.join(lines))
