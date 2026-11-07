# -*- coding: utf-8 -*-
"""Independent verification of fix_loc_g1.tsv."""
import io, os, re, json, sys, difflib

REV = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(REV, '..', '..'))
OUT = os.path.join(BASE, 'out', '02_戒疏')

def paras(chunk):
    txt = io.open(os.path.join(OUT, chunk + '.txt'), encoding='utf-8').read()
    return [x.strip() for x in re.split(r'\r?\n\s*\r?\n', txt) if x.strip()]

pc = {}
rows = []
with io.open(os.path.join(REV, 'fix_loc_g1.tsv'), encoding='utf-8') as f:
    raw = f.read()
print('trailing newline:', raw.endswith('\n'))
print('CR present:', '\r' in raw)
lines = [l for l in raw.split('\n') if l.strip()]
print('rows:', len(lines))
keys = set()
errs = []
for ln in lines:
    f2 = ln.split('\t')
    if len(f2) != 4:
        errs.append('bad field count %d: %s' % (len(f2), ln[:50]))
        continue
    book, chunk, seg, new = f2
    if book != '02_戒疏':
        errs.append('bad book ' + book)
    k = (chunk, seg)
    if k in keys:
        errs.append('dup key %s' % (k,))
    keys.add(k)
    if chunk not in pc:
        pc[chunk] = paras(chunk)
    i = int(seg) - 1
    if not (0 <= i < len(pc[chunk])):
        errs.append('seg out of range %s %s' % (chunk, seg))
        continue
    cur = pc[chunk][i]
    # label check
    lab = lambda s: s[:4] if s.startswith('【') else ''
    if lab(new) != lab(cur):
        errs.append('label mismatch %s %s: %s vs %s' % (chunk, seg, lab(cur), lab(new)))
    # common prefix/suffix
    sm = difflib.SequenceMatcher(None, cur, new)
    ops = [op for op in sm.get_opcodes() if op[0] != 'equal']
    changed = sum(max(o[2]-o[1], o[4]-o[3]) for o in ops)
    ratio = sm.ratio()
    print('%s seg=%-4s cur=%-5d new=%-5d ops=%d changed=%d ratio=%.3f' % (chunk, seg, len(cur), len(new), len(ops), changed, ratio))
    if len(new) < 0.7 * len(cur) or len(new) > 1.5 * len(cur):
        errs.append('length drift %s %s' % (chunk, seg))

print()
if errs:
    print('ERRORS:')
    for e in errs:
        print(' ', e)
    sys.exit(1)
print('VERIFY OK')
