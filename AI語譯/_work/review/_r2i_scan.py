# -*- coding: utf-8 -*-
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L

REVIEW = L.REVIEW_DIR
present = []
for n in range(1181, 1331):
    if os.path.exists(os.path.join(REVIEW, '校閱_%03d.txt' % n)):
        present.append(n)

recs = []
by_chunk = collections.OrderedDict()
for n in present:
    for r in L.parse_review(n):
        r['resp'] = n
        recs.append(r)
        by_chunk.setdefault(r['chunk'], []).append(r)

summary = []
for chunk, rs in by_chunk.items():
    o = L.load_out(chunk)
    segs = o['segs']
    print('=== %s  out_paras=%d  material_segs=%d (%d..%d)' % (
        chunk, len(segs), len(rs), rs[0]['resp'], rs[-1]['resp']))
    rows = []
    used = collections.defaultdict(list)
    for r in rs:
        s, pos = L.best_match(r['trans'], segs)
        r['pos'] = pos
        r['sim'] = round(s, 4)
        used[pos].append(r['uniq'])
        rows.append((r['resp'], r['uniq'], r['seg'], pos, round(s, 4)))
    low = [x for x in rows if x[4] < 0.94]
    dup = {k: v for k, v in used.items() if len(v) > 1}
    print('  low(<0.94): %d   dup_pos: %s' % (len(low), dup if dup else 'none'))
    for x in low:
        print('   LOW resp_%d %s material#%d -> out#%d sim=%.4f' % x)
    summary.append(dict(chunk=chunk, out_paras=len(segs), n=len(rs), low=len(low), dup=dup))

json.dump(dict(present=present, chunks=summary,
               recs=[{k: r[k] for k in ('resp','uniq','chunk','seg','orig','trans')} for r in recs]),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2i_scan.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nTOTAL files=%d segs=%d chunks=%d' % (len(present), len(recs), len(by_chunk)))
