# -*- coding: utf-8 -*-
"""掃描 校閱_1000..1648：每個檔的段標籤、書/chunk/段，檢查 out 檔存在與段數。"""
import os, re, json, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
REV = os.path.join(ROOT, '校閱_10K')
OUTBASE = os.path.join(ROOT, 'AI語譯', 'out')

LAB = re.compile(r'^【(\d{4})-(\d{4})】([^/]+)/([^#]+)#(\d+)\s*$')

def read(p):
    return open(p, 'rb').read().decode('utf-8')

def out_segs(book, chunk):
    p = os.path.join(OUTBASE, book, chunk + '.txt')
    if not os.path.exists(p):
        return None, None, None
    s = read(p)
    eol = '\r\n' if '\r\n' in s else '\n'
    parts = s.split(eol + eol)
    if parts and parts[-1] == '':
        parts = parts[:-1]
    return p, parts, eol

rows = []
missing_out = {}
bad = []
for n in range(1000, 1649):
    p = os.path.join(REV, '校閱_%d.txt' % n)
    if not os.path.exists(p):
        bad.append((n, 'NOFILE'))
        continue
    s = read(p)
    lines = s.split('\n')
    segs = []
    for ln in lines:
        ln = ln.rstrip('\r')
        m = LAB.match(ln)
        if m:
            n1, n2, book, chunk, seg = m.groups()
            segs.append(dict(batch=int(n1), seq=int(n2), book=book, chunk=chunk, seg=int(seg)))
    if not segs:
        bad.append((n, 'NOLABEL'))
        continue
    # 段序號必須 1..len 連續
    seqs = [x['seq'] for x in segs]
    if seqs != list(range(1, len(segs) + 1)):
        bad.append((n, 'SEQ:' + str(seqs[:5])))
    rows.append(dict(n=n, count=len(segs), book=segs[0]['book'], chunks=sorted(set(x['chunk'] for x in segs))))

# 檢查 out 段數
chunkinfo = {}
for r in rows:
    for c in r['chunks']:
        key = (r['book'], c)
        if key in chunkinfo:
            continue
        op, segs, eol = out_segs(*key)
        chunkinfo[key] = dict(exists=op is not None, n=(len(segs) if segs else 0),
                              eol=('CRLF' if eol == '\r\n' else 'LF') if eol else None, path=op)

print('files with labels:', len(rows))
print('bad:', bad[:20], 'total bad', len(bad))
bybook = {}
for r in rows:
    bybook.setdefault(r['book'], []).append(r['n'])
print('books:')
for b, ns in bybook.items():
    print('  %s: %d files, %d-%d' % (b, len(ns), min(ns), max(ns)))
tot = sum(r['count'] for r in rows)
print('total segments:', tot)
print('chunks:', len(chunkinfo))
print('missing out:', [(k, v) for k, v in chunkinfo.items() if not v['exists']])
json.dump(dict(rows=rows, chunkinfo={k[0] + '/' + k[1]: v for k, v in chunkinfo.items()}, bad=bad),
          open(os.path.join(os.path.dirname(__file__), '_r2a_plan.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('wrote _r2a_plan.json')
