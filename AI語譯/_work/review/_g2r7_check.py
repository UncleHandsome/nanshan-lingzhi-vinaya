# -*- coding: utf-8 -*-
import csv, io, sys, re
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'AI語譯/_work/review'
rows = list(csv.DictReader(io.open(BASE + r'/_g2r7_rows.tsv', encoding='utf-8', newline=''), delimiter='\t'))
cur = {(r['chunk'], r['seg']): r['current'] for r in rows}
outs = []
with io.open(BASE + r'/fix_re7_g2.tsv', encoding='utf-8', newline='') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        if not ln:
            continue
        p = ln.split('\t')
        outs.append((p[1], p[2], p[3]))

bad = []
for chunk, seg, t in outs:
    c = cur[(chunk, seg)]
    if t.count('「') != t.count('」'):
        bad.append(('quote', chunk, seg, t.count('「'), t.count('」')))
    if t.count('（') != t.count('）'):
        bad.append(('paren', chunk, seg, t.count('（'), t.count('）')))
    if t.count('『') != t.count('』'):
        bad.append(('dquote', chunk, seg, t.count('『'), t.count('』')))
    if re.search(r'。。|，，|；；|：：|、、|。。|」」|「「', t):
        bad.append(('dup', chunk, seg, re.search(r'。。|，，|；；|：：|、、|」」|「「', t).group(0)))
    # report changes in quote/paren balance vs current
    if (t.count('「') - c.count('「')) != (t.count('」') - c.count('」')):
        bad.append(('qdelta', chunk, seg))
print('bad:', bad if bad else 'NONE')

for k in [('03b_卷一之三', '9'), ('04b_卷一之四', '9'), ('04b_卷一之四', '135'),
          ('02a_卷一之二', '36'), ('02a_卷一之二', '48'), ('05a_卷一之五', '34'),
          ('00_卷首', '4'), ('03a_卷一之三', '48'), ('21a_卷四之四', '78'), ('01a_卷一之一', '24')]:
    t = dict(((a, b), x) for a, b, x in outs)[k]
    print('\n=== %s %s (len %d)' % (k[0], k[1], len(t)))
    print(t)
