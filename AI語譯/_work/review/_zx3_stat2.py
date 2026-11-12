# -*- coding: utf-8 -*-
"""重算已套用編輯（TSV 的 new 出現在現行段中）與 pre-edit 候選的採用／否決。"""
import os, re, json, glob, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import _r2a_lib as L

applied = {}
d = json.load(open(os.path.join(BASE, 'edits_1073.json'), encoding='utf-8-sig'))
for e in d['edits']:
    applied.setdefault(1073, []).append(dict(chunk=e['chunk'], seg=e['seg'], old=e['old'], new=e['new']))

cache = {}
def segs_of(book, chunk):
    k = (book, chunk)
    if k not in cache:
        cache[k] = L.Out(book, chunk).segs
    return cache[k]

skipped = []
for tp in sorted(glob.glob(os.path.join(BASE, '_zx3_b*.tsv'))):
    for ln in open(tp, encoding='utf-8-sig'):
        ln = ln.rstrip('\n').rstrip('\r')
        if not ln.strip() or ln.startswith('#'):
            continue
        p = ln.split('|||')
        n = int(p[0]); seq = int(p[1]); old = p[2]; new = p[3]
        m = {r['seq']: (r['book'], r['chunk'], r['seg']) for r in L.parse_review(n)}
        if seq not in m:
            skipped.append((n, seq, old, 'BADSEQ')); continue
        book, chunk, seg = m[seq]
        segs = segs_of(book, chunk)
        if new in segs[seg - 1]:
            applied.setdefault(n, []).append(dict(chunk=chunk, seg=seg, old=old, new=new))
            continue
        found = [i + 1 for i, t in enumerate(segs) if new in t]
        if len(found) == 1:
            applied.setdefault(n, []).append(dict(chunk=chunk, seg=found[0], old=old, new=new))
        else:
            skipped.append((n, seq, old, 'NOTFOUND%s' % found))

# 1145 的修正（TSV 的 new 非精確子串，於覆核後改寫為整句）
applied.setdefault(1145, []).append(dict(chunk='08c_中二', seg=41,
    old='這五種因緣正好反顯前面的第二種犯戒因緣',
    new='這五種因緣正好與前面第二種犯緣相反（故不犯）'))

# pre-edit candidates
raw = open(os.path.join(BASE, '_zx3_cand_pre.txt'), 'rb').read()
try: txt = raw.decode('utf-8')
except Exception: txt = raw.decode('utf-16')
cand = {}
for ln in txt.splitlines():
    if re.match(r'^\d+\|', ln):
        p = ln.split('|')
        cand.setdefault(int(p[0]), []).append((int(p[2]), p[3]))

rows = []
tot = dict(files=0, cand=0, edits=0, segs=0, used=0, rej=0)
chunk_stat = {}
for n in range(1073, 1181):
    if n in (1086, 1105):
        continue
    es = applied.get(n, [])
    cs = cand.get(n, [])
    used = 0
    for seg, old in cs:
        if any((old in e['old']) or (e['old'] in old) for e in es):
            used += 1
    segs = set((e['chunk'], e['seg']) for e in es)
    rows.append((n, len(cs), used, len(segs), len(es), len(cs) - used))
    tot['files'] += 1; tot['cand'] += len(cs); tot['edits'] += len(es)
    tot['segs'] += len(segs); tot['used'] += used; tot['rej'] += len(cs) - used
    for k, s in segs:
        chunk_stat.setdefault(k, [0, 0])
        chunk_stat[k][0] += 1
    for e in es:
        chunk_stat.setdefault(e['chunk'], [0, 0])
        chunk_stat[e['chunk']][1] += 1

print('files', tot['files'], 'edits', tot['edits'], 'segs', tot['segs'], 'cand', tot['cand'], 'used', tot['used'], 'rej', tot['rej'])
print('skipped rows', len(skipped))
json.dump(dict(rows=rows, chunk_stat=chunk_stat, tot=tot), open(os.path.join(BASE, '_zx3_stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
