import io, json, re
HERE = r'AI語譯\_work\review'
rows = json.load(io.open(HERE + r'\_g2_base.json', encoding='utf-8'))
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
rows.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
lines = [l for l in io.open(HERE + r'\fix_loc_g2.tsv', encoding='utf-8').read().split('\n') if l.strip()]
done = set()
for l in lines:
    f = l.split('\t'); done.add((f[0], f[1], f[2]))
q = re.compile(r'[「『]([^「」『』]{2,40})[」』]')
skipped = []
for i, r in enumerate(rows, 1):
    k = (r['book'], r['chunk'], r['seg'])
    if k in done: continue
    qs = [x for x in q.findall(r['problem']) + q.findall(r['suggestion']) if len(x) >= 3]
    hits = [x for x in qs if x in r['cur2']]
    skipped.append((i, r['book'], r['chunk'], r['seg'], len(hits), len(qs), hits[:3]))
print('skipped', len(skipped))
out = []
for s in skipped:
    out.append('row %2d  %s %s#%s  hits=%d/%d  %s' % (s[0], s[1], s[2], s[3], s[4], s[5], ' | '.join(s[6])))
io.open(HERE + r'\_g2_skip.txt','w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
