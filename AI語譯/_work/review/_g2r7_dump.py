import csv, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/_g2r7_rows.tsv'
rows = list(csv.DictReader(open(p, encoding='utf-8', newline=''), delimiter='\t'))
# group by (chunk, seg) preserving first-appearance order
groups = collections.OrderedDict()
for r in rows:
    key = (r['chunk'], r['seg'])
    groups.setdefault(key, []).append(r)
print('groups', len(groups))
# chunk distribution
cc = collections.Counter(r['chunk'] for r in rows)
for k, v in cc.items():
    print(k, v)
# write grouped dump in batches of 16 groups
items = list(groups.items())
batch = 16
import os
os.makedirs('AI語譯/_work/review/_g2r7_batch', exist_ok=True)
for bi in range(0, len(items), batch):
    part = items[bi:bi+batch]
    lines = []
    for key, rs in part:
        lines.append('='*100)
        lines.append(f"### chunk={key[0]} seg={key[1]}  rows={[r['ridx'] for r in rs]}")
        for r in rs:
            lines.append(f"-- ridx {r['ridx']} | level={r['level']} | cls={r['cls']} | gid={r['gid']}")
            lines.append(f"[problem] {r['problem']}")
            lines.append(f"[suggestion] {r['suggestion']}")
        lines.append(f"[CURRENT] {rs[0]['current']}")
        lines.append('')
    fn = f'AI語譯/_work/review/_g2r7_batch/b{bi//batch:02d}.txt'
    open(fn, 'w', encoding='utf-8').write('\n'.join(lines))
    print(fn, len(part), 'groups')
