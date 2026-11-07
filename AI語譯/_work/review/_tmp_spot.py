import io, json
HERE = r'AI語譯\_work\review'
rows = json.load(io.open(HERE + r'\_g2_base.json', encoding='utf-8'))
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
rows.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
out = []
for i in [60, 74, 86, 89, 90, 91, 92]:
    r = rows[i-1]
    out.append('='*80)
    out.append('[%d] %s %s#%s  len=%d' % (i, r['book'], r['chunk'], r['seg'], len(r['cur2'])))
    out.append('P: ' + r['problem'])
    out.append('S: ' + r['suggestion'])
    out.append('ORIG: ' + r['orig'])
    out.append('C: ' + r['cur2'])
io.open(HERE + r'\_g2_spot.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
