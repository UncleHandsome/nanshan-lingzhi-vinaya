import json, re

p = r'AI語譯\_work\review\report_re9.tsv'
rows = []
with open(p, encoding='utf-8-sig') as f:
    lines = f.read().split('\n')
hdr = lines[0].split('\t')
for ln in lines[1:]:
    if not ln.strip():
        continue
    f = ln.split('\t')
    if len(f) != 10:
        print('BADFIELDS', len(f), f[0])
        continue
    d = dict(zip(hdr, f))
    if d['book'] in ('01_行事鈔', '03_業疏'):
        rows.append(d)
print('ROWS', len(rows))
json.dump(rows, open(r'AI語譯\_work\review\tmp_g3_rows.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i, d in enumerate(rows):
    qp = [q for q in re.findall(r'「([^」]*)」', d['problem']) if q in d['current']]
    print(i, d['gid'], d['book'], d['chunk'], d['seg'], d['level'], d['cls'], 'len', len(d['current']), 'match', len(qp))
    for q in qp[:3]:
        print('   HIT:', q[:60])
