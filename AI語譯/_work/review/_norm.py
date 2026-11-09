# -*- coding: utf-8 -*-
import csv, json, io

P = r'AI語譯/_work/review/report_re7.tsv'
rows = []
with open(P, encoding='utf-8', newline='') as f:
    rd = csv.reader(f, delimiter='\t'); next(rd)
    for r in rd:
        rows.append(r)
J = [r for r in rows if r[1] == '02_戒疏']
sts = json.load(open(r'AI語譯/_work/review/_tmp_status.json', encoding='utf-8'))

def q_to_angle(s):
    return s.replace('『', '「').replace('』', '」')

def q_to_corner(s):
    return s.replace('「', '『').replace('」', '』')

ids = [s['idx'] for s in sts if s['status'] == 'MISS']
out = io.open(r'AI語譯/_work/review/_tmp_miss3.txt', 'w', encoding='utf-8')
resolved = 0
for st in sts:
    if st['status'] != 'MISS':
        continue
    cur = J[st['idx']][9]
    old, new = st['pairs'][0]
    tag = None
    if old in cur:
        tag = 'exact'
    elif q_to_angle(old) in cur:
        tag = 'angle'
    elif q_to_corner(old) in cur:
        tag = 'corner'
    if tag:
        resolved += 1
    else:
        out.write('--- idx %d gid %s seg %s\nOLD: %s\nNEW: %s\n' % (st['idx'], st['gid'], st['seg'], old, new))
out.close()
print('resolved by quote-normalize:', resolved, 'still unresolved:', len(ids) - resolved)
