import json, re, sys

rows = json.load(open(r'AI語譯\_work\review\tmp_g3_rows.json', encoding='utf-8'))
out = []
for i, d in enumerate(rows):
    out.append('=' * 20)
    out.append(f"[{i}] {d['gid']} {d['book']} {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}")
    out.append('PROBLEM: ' + d['problem'])
    out.append('SUGGESTION: ' + d['suggestion'])
    qp = re.findall(r'「([^」]*)」', d['problem'])
    hits = [q for q in qp if q in d['current']]
    out.append('PROB_QUOTES: ' + ' | '.join(qp))
    out.append('PROB_HITS_IN_CURRENT: ' + (' || '.join(hits) if hits else '(none)'))
    sq = re.findall(r'「([^」]*)」', d['suggestion'])
    for s in sq:
        out.append('  SUG_QUOTE: ' + s + '   [in_current=' + str(s in d['current']) + ']')
    out.append('CURRENT_LEN: ' + str(len(d['current'])))
open(r'AI語譯\_work\review\tmp_g3_digest.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote', len(rows))
