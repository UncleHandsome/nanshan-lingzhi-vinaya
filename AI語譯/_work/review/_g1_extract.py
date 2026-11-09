# -*- coding: utf-8 -*-
import re, json, collections

SRC = 'AI語譯/_work/review/report_re6.tsv'
rows = [l.split('\t') for l in open(SRC, encoding='utf-8').read().split('\n')[1:] if l.strip()]
sel = [r for r in rows if len(r) == 10 and r[1] == '02_戒疏']

Q = re.compile(r'[「『]([^「」『』]+)[」』]')


def pairs_from_suggestion(sug):
    """Return list of (sources(list), target) from 改為 constructs."""
    out = []
    for m in re.finditer(r'(改為|修改為|改作|改譯為|應改為)', sug):
        start = m.start()
        end = m.end()
        # text before (limit 60 chars)
        before = sug[max(0, start - 60):start]
        after = sug[end:]
        # target: first quoted string right after, allowing ：，、 and space
        mt = re.match(r'[：:，,、\s]*[「『]([^「」『』]+)[」』]', after)
        if not mt:
            continue
        target = mt.group(1)
        # sources: quoted strings in `before`, split by separators; take trailing run
        srcs = Q.findall(before)
        if not srcs:
            continue
        # keep only the trailing consecutive quoted items (e.g. 將「A」、「B」皆)
        # simple heuristic: use last one, plus any earlier ones if separated only by 、,，且兩處
        srcs = [srcs[-1]]
        out.append((srcs, target))
    return out


def apply_pairs(text, pairs):
    log = []
    for srcs, tgt in pairs:
        ok = False
        for s in srcs:
            if s in text:
                text = text.replace(s, tgt)
                ok = True
        log.append((srcs, tgt, ok))
    return text, log


data = []
for i, r in enumerate(sel):
    gid, book, chunk, seg, level, cls, prob, sug, orig, cur = r
    data.append(dict(idx=i, gid=gid, chunk=chunk, seg=seg, level=level, cls=cls,
                     prob=prob, sug=sug, orig=orig, cur=cur))

results = []
for d in data:
    sug = d['sug'].strip()
    if not sug:
        d['status'] = 'nosug'
        results.append(d)
        continue
    pairs = pairs_from_suggestion(sug)
    if not pairs:
        d['status'] = 'nopair'
        results.append(d)
        continue
    new, log = apply_pairs(d['cur'], pairs)
    d['pairs'] = pairs
    d['new'] = new
    if all(x[2] for x in log):
        d['status'] = 'auto'
    else:
        d['status'] = 'partial'
    results.append(d)

json.dump(results, open('AI語譯/_work/review/_g1_data.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print(collections.Counter(d['status'] for d in results))
