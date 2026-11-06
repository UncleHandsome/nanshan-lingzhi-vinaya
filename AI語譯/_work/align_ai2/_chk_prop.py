import io, json, os
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '_tmp_a2prop.json')
d = json.load(io.open(p, encoding='utf-8'))
raw = d['raw']; cl = d['clamped']
print('raw n=%d  range %d..%d' % (len(raw), min(x[1] for x in raw), max(x[1] for x in raw)))
print('clamped n=%d range %d..%d distinct=%d' % (len(cl), min(x[1] for x in cl), max(x[1] for x in cl), len(set(x[1] for x in cl))))
print('raw sample', [list(x) for x in raw[::20]])
print('clamped sample', [list(x) for x in cl[::20]])
