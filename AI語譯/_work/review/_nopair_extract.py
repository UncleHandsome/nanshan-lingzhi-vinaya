# -*- coding: utf-8 -*-
import csv, json, io, re

P = r'AI語譯/_work/review/report_re7.tsv'
rows = []
with open(P, encoding='utf-8', newline='') as f:
    rd = csv.reader(f, delimiter='\t'); next(rd)
    for r in rd:
        rows.append(r)
J = [r for r in rows if r[1] == '02_戒疏']
sts = json.load(open(r'AI語譯/_work/review/_tmp_status.json', encoding='utf-8'))

def norm(s):
    return s.replace('『', '「').replace('』', '」')

def quotes(s):
    qs = re.findall(r'「([^「」]*)」', s) + re.findall(r'『([^『』]*)』', s)
    # also single quotes used in report? use ‘ ’ maybe
    return qs

out = io.open(r'AI語譯/_work/review/_tmp_nopair2.txt', 'w', encoding='utf-8')
nomatch = []
for st in sts:
    if st['status'] != 'NOPAIR':
        continue
    r = J[st['idx']]
    cur = r[9]
    prob = r[6]
    sug = r[7]
    qs = [q for q in quotes(prob) if len(q) >= 4]
    found = []
    for q in qs:
        if q in cur:
            found.append((len(q), q, 'exact'))
        elif norm(q) in norm(cur):
            found.append((len(q), q, 'norm'))
    found.sort(reverse=True)
    out.write('=== idx %d gid %s chunk %s seg %s | quotes=%d matched=%d\n' % (st['idx'], st['gid'], r[2], r[3], len(qs), len(found)))
    if found:
        out.write('MATCH: %s\n' % found[0][1])
        # sentence containing
        q = found[0][1]
        i = cur.find(q)
        if i < 0:
            i = norm(cur).find(norm(q))
        s = max(0, cur.rfind('。', 0, i) + 1)
        e = cur.find('。', i + len(q))
        e = len(cur) if e < 0 else e + 1
        out.write('SENT> %s\n' % cur[s:e])
    else:
        nomatch.append(st['idx'])
        out.write('NOMATCH quotes: %s\n' % ' | '.join(qs[:5]))
    out.write('SUG: %s\n' % sug)
    out.write('\n')
out.close()
print('nomatch', len(nomatch), nomatch)
