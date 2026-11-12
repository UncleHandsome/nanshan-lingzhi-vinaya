# -*- coding: utf-8 -*-
import json, os, collections
from _r2z4_lib import parse_review, load_out, BK_DIR

chunks = ['02b_上一下', '02c_上一下', '02d_上一下', '02e_上一下', '02f_上一下',
          '03a_上二', '03b_上二', '03c_上二', '03d_上二', '04a_上三', '04b_上三']
cov = collections.Counter(); files = collections.defaultdict(set)
for n in range(926, 1000):
    p = '../../../batch_qwen/r2/resp_%03d.txt' % n
    if not os.path.exists(p):
        continue
    for r in parse_review(n):
        cov[r['chunk']] += 1
        files[r['chunk']].add(n)
log = [json.loads(l) for l in open('_r2z4_log.jsonl', encoding='utf-8')]
ec = collections.Counter(x['chunk'] for x in log)


def split(s, eol):
    parts = s.split(eol + eol)
    if parts and parts[-1] == '':
        parts = parts[:-1]
    elif parts and parts[-1].endswith(eol):
        parts[-1] = parts[-1][:-len(eol)]
    return parts


rows = []
for c in chunks:
    cur = load_out(c)
    b = open(os.path.join(BK_DIR, c + '_f.txt'), 'rb').read().decode('utf-8')
    eol = '\r\n' if '\r\n' in b else '\n'
    bs = split(b, eol)
    d = [i + 1 for i, (x, y) in enumerate(zip(cur['segs'], bs)) if x != y]
    rows.append((c, len(cur['segs']), cov[c], len(d), ec[c], len(files[c])))
    print('| %s | %d | %d | %d | %d | %d |' % (c, len(cur['segs']), cov[c], len(d), ec[c], len(files[c])))
print('TOTAL', sum(r[1] for r in rows), sum(r[2] for r in rows), sum(r[3] for r in rows), sum(r[4] for r in rows))
