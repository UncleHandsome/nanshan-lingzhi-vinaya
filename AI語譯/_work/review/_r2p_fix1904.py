# -*- coding: utf-8 -*-
"""One-off: apply 3 extra edits to n=1904, merging with existing log/stats."""
import os, sys, json, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

N = 1904
NEW = [
    (3, "雖然開許面對別眾乃至一人", "雖然開許對別人（眾多人或一人）", "別眾應作別人"),
    (5, "所說的犯戒通於全僧與別眾個人", "所說的犯戒通於僧與別人（眾多人、一人）", "別眾應作別人"),
    (17, "在道理上絕非向別眾除罪", "在道理上絕非向別人除罪", "別眾應作別人"),
]
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log', 'log_%d.json' % N)
STAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2p_stats.jsonl')
d = json.load(open(LOG, encoding='utf-8'))
recs = {r['seq']: r for r in L.parse_review(N)}
o = L.Out('03_業疏', '22b_卷四之五')
segs = list(o.segs)
logs = list(d['edits'])
for seq, old, new, why in NEW:
    r = recs[seq]
    i = r['seg'] - 1
    t = segs[i]
    assert t.count(old) == 1, (seq, old)
    nl = t.count('\n')
    t2 = t.replace(old, new)
    assert t2.count('\n') == nl
    segs[i] = t2
    logs.append(dict(book=r['book'], chunk=r['chunk'], seg=r['seg'], old=old, new=new, why=why))
o.segs = segs
o.save()
d['edits'] = logs
d['verdicts'] = d['verdicts'] + [dict(seq=x[0], kind='真錯', reason=x[3]) for x in NEW]
json.dump(d, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
kinds = {}
for v in d['verdicts']:
    kinds[v['kind']] = kinds.get(v['kind'], 0) + 1
rows = [json.loads(l) for l in open(STAT, encoding='utf-8')]
for row in rows:
    if row['n'] == N:
        row['segs'] = len(set(e['seg'] for e in logs))
        row['edits'] = len(logs)
        row['kinds'] = kinds
with open(STAT, 'w', encoding='utf-8') as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
print('OK', N, 'edits', len(logs), 'segs', len(set(e['seg'] for e in logs)))
