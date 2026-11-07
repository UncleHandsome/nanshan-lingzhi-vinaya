# -*- coding: utf-8 -*-
"""Extract real current translations for g1 (02_戒疏) rows."""
import io, os, re, json, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REV = os.path.join(BASE, '_work', 'review')
SRC = os.path.join(REV, 'located_all.tsv')
OUT = os.path.join(BASE, 'out')

rows = []
with io.open(SRC, encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        line = line.rstrip('\n')
        if not line:
            continue
        f2 = line.split('\t')
        if len(f2) != len(hdr):
            continue
        d = dict(zip(hdr, f2))
        if int(d['votes']) >= 3 and d['book'] == '02_戒疏':
            rows.append(d)

print('selected', len(rows))

# pack parsing: blocks like 【段1009】02_戒疏/03a_卷一下之一#4\n【原文】...\n【譯文】...
blocks = {}
for pk in set(r['pack'] for r in rows):
    p = os.path.join(REV, 'pack', 'in', pk)
    txt = io.open(p, encoding='utf-8').read()
    for m in re.finditer(r'【段(\d+)】([^\n#]+)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【段|\Z)', txt, re.S):
        segno, bookpath, seg, orig, tr = m.groups()
        book, chunk = bookpath.split('/')
        blocks[(book, chunk, seg)] = dict(segno=segno, orig=orig.strip(), tr=tr.strip(), pack=pk)

print('pack blocks', len(blocks))

# out paragraphs
def paras(book, chunk):
    p = os.path.join(OUT, book, chunk + '.txt')
    if not os.path.exists(p):
        return None
    txt = io.open(p, encoding='utf-8').read()
    return [x.strip() for x in re.split(r'\r?\n\s*\r?\n', txt) if x.strip()]

pcache = {}
res = []
for r in rows:
    chunk = r['chunk']
    key = (r['book'], chunk, r['seg'])
    b = blocks.get(key)
    if chunk not in pcache:
        pcache[chunk] = paras(r['book'], chunk)
    ps = pcache[chunk]
    i = int(r['seg']) - 1
    outp = ps[i] if ps and 0 <= i < len(ps) else None
    res.append(dict(pack=r['pack'], chunk=chunk, seg=r['seg'], level=r['level'], cls=r['cls'],
                    problem=r['problem'], suggestion=r['suggestion'], orig=r['orig'],
                    located_current=r['current'],
                    pack_orig=b['orig'] if b else None,
                    pack_tr=b['tr'] if b else None,
                    out_para=outp,
                    orig_match=(b is not None and b['orig'] == r['orig']),
                    out_vs_pack=(b is not None and outp is not None and outp == b['tr'])))

print('missing block:', sum(1 for x in res if x['pack_tr'] is None))
print('orig match pack:', sum(1 for x in res if x['orig_match']))
print('out==pack_tr:', sum(1 for x in res if x['out_vs_pack']))

json.dump(res, io.open(os.path.join(REV, '_g1b_sel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# dump readable
with io.open(os.path.join(REV, '_g1b_dump.txt'), 'w', encoding='utf-8') as w:
    for i, x in enumerate(res, 1):
        w.write('=' * 90 + '\n')
        w.write('[%d] pack=%s %s seg=%s level=%s cls=%s\n' % (i, x['pack'], x['chunk'], x['seg'], x['level'], x['cls']))
        w.write('PROBLEM : %s\n' % x['problem'])
        w.write('SUGGEST : %s\n' % x['suggestion'])
        w.write('ORIG    : %s\n' % x['orig'])
        w.write('PKTR    : %s\n' % x['pack_tr'])
        w.write('OUTPARA : %s\n' % x['out_para'])
        if not x['orig_match']:
            w.write('!! ORIG != PACK ORIG: %s\n' % x['pack_orig'])
        if not x['out_vs_pack']:
            w.write('!! OUT != PACK TR\n')
print('dumped')
