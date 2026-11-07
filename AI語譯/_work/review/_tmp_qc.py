import io, json, re, sys
HERE = r'AI語譯\_work\review'
rows = json.load(io.open(HERE + r'\_g2_base.json', encoding='utf-8'))
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
rows.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
q = re.compile(r'[「『]([^「」『』]{2,40})[」』]')
out = []
for i, r in enumerate(rows, 1):
    cur = r['cur2']
    qs = [x for x in q.findall(r['problem']) + q.findall(r['suggestion']) if len(x) >= 3]
    hits = [x for x in qs if x in cur]
    out.append('%2d %s %s#%s len=%d nq=%d hits=%d' % (i, r['book'], r['chunk'], r['seg'], len(cur), len(qs), len(hits)))
    for x in qs:
        out.append('     %s %s' % ('OK ' if x in cur else 'MISS', x))
io.open(HERE + r'\_g2_qcheck.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')
