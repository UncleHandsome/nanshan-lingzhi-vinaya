# -*- coding: utf-8 -*-
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L

REVIEW = L.REVIEW_DIR
present = [n for n in range(1181, 1331) if os.path.exists(os.path.join(REVIEW, '校閱_%03d.txt' % n))]
recs = []
by_chunk = collections.OrderedDict()
for n in present:
    for r in L.parse_review(n):
        r['resp'] = n
        recs.append(r)
        by_chunk.setdefault(r['chunk'], []).append(r)

for chunk, rs in by_chunk.items():
    o = L.load_out(chunk)
    segs = o['segs']
    deltas = []
    for r in rs:
        s, pos = L.best_match(r['trans'], segs)
        r['pos'] = pos; r['sim'] = round(s, 4)
        deltas.append(pos - r['seg'])
    c = collections.Counter(deltas)
    print('%-12s n=%2d out=%2d  seg:%d..%d  pos:%d..%d  delta=%s' % (
        chunk, len(rs), len(segs), rs[0]['seg'], rs[-1]['seg'], rs[0]['pos'], rs[-1]['pos'],
        dict(c)))
    bad = [r for r in rs if r['pos'] - r['seg'] != c.most_common(1)[0][0]]
    for r in bad:
        print('    ODD %s material#%d -> out#%d sim=%.4f' % (r['uniq'], r['seg'], r['pos'], r['sim']))
json.dump([{k: r[k] for k in ('resp','uniq','chunk','seg','orig','trans','pos','sim')} for r in recs],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2i_map.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('saved _r2i_map.json  recs=%d' % len(recs))
