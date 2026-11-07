import io, json
HERE = r'AI語譯\_work\review'
rows = json.load(io.open(HERE + r'\_g2_base.json', encoding='utf-8'))
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
rows.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
lines = io.open(HERE + r'\fix_loc_g2.tsv', encoding='utf-8').read().split('\n')
lines = [l for l in lines if l.strip()]
print('output rows', len(lines))
idx = {}
for l in lines:
    f = l.split('\t')
    idx[(f[0], f[1], f[2])] = f[3]
bad = [l for l in lines if len(l.split('\t')) != 4]
print('bad field count', len(bad))
out = []
for i in [11, 15, 30, 33, 42, 43, 71, 74, 89, 96]:
    r = rows[i-1]
    k = (r['book'], r['chunk'], r['seg'])
    out.append('#### row %d %s %s#%s' % (i, r['book'], r['chunk'], r['seg']))
    out.append(idx[k])
    out.append('')
io.open(HERE + r'\_g2_review.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok')
