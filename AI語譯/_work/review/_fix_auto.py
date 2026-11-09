# -*- coding: utf-8 -*-
import csv, re, io, json, os

P = r'AI語譯/_work/review/report_re7.tsv'
rows = []
with open(P, encoding='utf-8', newline='') as f:
    rd = csv.reader(f, delimiter='\t')
    next(rd)
    for r in rd:
        rows.append(r)
J = [r for r in rows if r[1] == '02_戒疏']

pair_re = re.compile(r'「([^「」]*)」\s*(?:改|修正|改譯)為\s*「([^「」]*)」')

def parse(r):
    s = r[7].strip()
    if not s:
        return None
    pairs = pair_re.findall(s)
    return pairs or None

out = []
for i, r in enumerate(J):
    cur = r[9]
    pairs = parse(r)
    rec = {'idx': i, 'gid': r[0], 'chunk': r[2], 'seg': r[3], 'status': '', 'pairs': pairs, 'sug': r[7].strip()}
    if pairs is None:
        rec['status'] = 'NOPAIR' if r[7].strip() else 'EMPTY'
    else:
        st = []
        for old, new in pairs:
            if old in cur:
                st.append('OLDFOUND')
            elif new and new in cur:
                st.append('ALREADY')
            else:
                st.append('MISS')
        rec['status'] = ','.join(st)
    out.append(rec)

from collections import Counter
print(Counter(x['status'] for x in out))
json.dump(out, open(r'AI語譯/_work/review/_tmp_status.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
