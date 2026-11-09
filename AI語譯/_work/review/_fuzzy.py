# -*- coding: utf-8 -*-
import csv, re, json, io, difflib

P = r'AI語譯/_work/review/report_re7.tsv'
rows = []
with open(P, encoding='utf-8', newline='') as f:
    rd = csv.reader(f, delimiter='\t'); next(rd)
    for r in rd:
        rows.append(r)
J = [r for r in rows if r[1] == '02_戒疏']
sts = json.load(open(r'AI語譯/_work/review/_tmp_status.json', encoding='utf-8'))

def best_match(s, cur):
    sm = difflib.SequenceMatcher(None, s, cur, autojunk=False)
    m = sm.find_longest_match(0, len(s), 0, len(cur))
    if m.size == 0:
        return None, 0
    # extend window around match to length of s
    start = m.b - m.a
    start = max(0, min(start, len(cur) - len(s))) if len(cur) > len(s) else 0
    window = cur[start:start+len(s)]
    ratio = difflib.SequenceMatcher(None, s, window, autojunk=False).ratio()
    return window, ratio

out = io.open(r'AI語譯/_work/review/_tmp_miss2.txt', 'w', encoding='utf-8')
for st in sts:
    if st['status'] != 'MISS':
        continue
    r = J[st['idx']]
    cur = r[9]
    old, new = st['pairs'][0]
    w1, r1 = best_match(old, cur)
    w2, r2 = best_match(new, cur)
    out.write('--- idx %d gid %s seg %s  OLDsim=%.2f NEWsim=%.2f\n' % (st['idx'], st['gid'], st['seg'], r1, r2))
    out.write('OLD> %s\n' % old)
    out.write('WIN> %s\n' % (w1 or ''))
    out.write('NEW> %s\n' % new)
    if r2 > r1:
        out.write('NEWWIN> %s\n' % (w2 or ''))
    out.write('\n')
out.close()
print('ok')
