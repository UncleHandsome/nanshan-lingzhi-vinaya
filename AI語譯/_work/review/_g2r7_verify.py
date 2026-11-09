# -*- coding: utf-8 -*-
import csv, io, sys, difflib
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'AI語譯/_work/review'
rows = list(csv.DictReader(io.open(BASE + r'/_g2r7_rows.tsv', encoding='utf-8', newline=''), delimiter='\t'))
cur = {}
for r in rows:
    cur[(r['chunk'], r['seg'])] = r['current']
outs = []
with io.open(BASE + r'/fix_re7_g2.tsv', encoding='utf-8', newline='') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        if not ln:
            continue
        parts = ln.split('\t')
        assert len(parts) == 4, (len(parts), ln[:60])
        assert parts[0] == '03_業疏'
        outs.append((parts[1], parts[2], parts[3]))
print('lines', len(outs))
same = 0
for chunk, seg, text in outs:
    c = cur[(chunk, seg)]
    if text == c:
        same += 1
        print('SAME AS CURRENT:', chunk, seg)
print('same:', same)

# show diffs
for chunk, seg, text in outs:
    c = cur[(chunk, seg)]
    sm = difflib.SequenceMatcher(None, c, text, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
    print('###', chunk, seg, 'diffs=', len(ops))
    for tag, i1, i2, j1, j2 in ops:
        print('  -', repr(c[max(0,i1-12):i2+12]))
        print('  +', repr(text[max(0,j1-12):j2+12]))
