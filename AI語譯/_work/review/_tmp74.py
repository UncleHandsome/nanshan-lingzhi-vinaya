import io, json
HERE = r'AI語譯\_work\review'
rows = json.load(io.open(HERE + r'\_g2_base.json', encoding='utf-8'))
ORDER = ['資持記', '01_行事鈔', '04_比丘尼鈔', '05_拾毗尼義鈔']
rows.sort(key=lambda r: (ORDER.index(r['book']), r['chunk'], int(r['seg']) if r['seg'].isdigit() else 0))
r = rows[73]
c = r['cur2']
out = []
out.append('LEN %d' % len(c))
for kw in ['一切捨','五種長物','同心淨人','重重','百一']:
    idx = 0
    while True:
        p = c.find(kw, idx)
        if p < 0: break
        out.append('%s @%d : %s' % (kw, p, c[max(0,p-60):p+80]))
        idx = p+1
out.append('--- TAIL 1000 ---')
out.append(c[-1000:])
io.open(HERE + r'\_g2_74.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok')
