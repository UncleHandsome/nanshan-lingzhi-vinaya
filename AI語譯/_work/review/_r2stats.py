# -*- coding: utf-8 -*-
import json, glob, os, collections, io

d = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_zx1389_e'
files = []
for p in sorted(glob.glob(os.path.join(d, '*.json'))):
    n = int(os.path.basename(p)[:-5])
    if 1389 <= n <= 1490:
        files.append((n, p))

tot_e = tot_r = tot_d = 0
segs = collections.Counter()
per = []
for n, p in files:
    j = json.load(open(p, encoding='utf-8'))
    e = len(j.get('edits', []))
    r = len(j.get('rejected', []))
    dd = len(j.get('doubt', []))
    tot_e += e
    tot_r += r
    tot_d += dd
    for x in j.get('edits', []):
        segs[(x['book'], x['chunk'], x['seg'])] += 1
    per.append((n, e, r, dd))

print('files', len(files))
print('edits', tot_e, 'rejected', tot_r, 'doubt', tot_d)
print('unique segs', len(segs))
books = collections.Counter(k[0] for k in segs)
chunks = collections.Counter((k[0], k[1]) for k in segs)
print(books)
for k, v in chunks.items():
    print(k, v)
print('missing n:', [x for x in range(1389, 1491) if x not in [f[0] for f in files]])
