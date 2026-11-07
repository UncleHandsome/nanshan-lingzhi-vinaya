# -*- coding: utf-8 -*-
"""Show change context for each fixed row."""
import io, os, re, json, difflib
REV = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.abspath(os.path.join(REV, '..', '..')), 'out', '02_戒疏')
pc = {}
def paras(chunk):
    if chunk not in pc:
        txt = io.open(os.path.join(OUT, chunk + '.txt'), encoding='utf-8').read()
        pc[chunk] = [x.strip() for x in re.split(r'\r?\n\s*\r?\n', txt) if x.strip()]
    return pc[chunk]

rows = [(l.split('\t')[1], l.split('\t')[2], l.split('\t')[3]) for l in io.open(os.path.join(REV, 'fix_loc_g1.tsv'), encoding='utf-8').read().split('\n') if l.strip()]
w = io.open(os.path.join(REV, '_g1b_ctx.txt'), 'w', encoding='utf-8')
for chunk, seg, new in rows:
    cur = paras(chunk)[int(seg) - 1]
    sm = difflib.SequenceMatcher(None, cur, new)
    w.write('== %s seg=%s\n' % (chunk, seg))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        a = cur[max(0, i1-18):i1]
        b = cur[i2:i2+18]
        w.write('  [%s] ..%s【%s】%s.. -> 【%s】\n' % (tag, a, cur[i1:i2], b, new[j1:j2]))
    w.write('\n')
w.close()
print('ok', len(rows))
