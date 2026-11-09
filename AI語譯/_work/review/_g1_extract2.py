# -*- coding: utf-8 -*-
import json, re, collections

d = json.load(open('AI語譯/_work/review/_g1_data.json', encoding='utf-8'))

OPEN = '「『'
CLOSE = '」』'
CHANGE = ('改為', '修改為', '改作', '改譯為')


def spans(s):
    """return list of (start,end,content) for outermost quoted spans"""
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] in OPEN:
            op = s[i]
            cl = CLOSE[OPEN.index(op)]
            depth = 1
            j = i + 1
            while j < n and depth:
                if s[j] == op:
                    depth += 1
                elif s[j] == cl:
                    depth -= 1
                j += 1
            if depth == 0:
                out.append((i, j, s[i + 1:j - 1]))
            i = j
        else:
            i += 1
    return out


def extract(sug):
    pairs = []
    for m in re.finditer('|'.join(CHANGE), sug):
        cstart, cend = m.start(), m.end()
        before = sug[:cstart]
        after = sug[cend:]
        # source = last quoted span in before
        bs = [x for x in spans(before) if x[1] <= len(before)]
        if not bs:
            continue
        src = bs[-1][2]
        # target = first quoted span in after, near start
        at = re.match(r'[：:，,、\s]*', after)
        k = at.end()
        ts = [x for x in spans(after) if x[0] == k or x[0] <= k + 2]
        if not ts:
            continue
        tgt = ts[0][2]
        pairs.append((src, tgt))
    # dedupe
    seen = set()
    out = []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


res = []
for x in d:
    if x['status'] in ('auto', 'nosug'):
        continue
    p = extract(x['sug'])
    x['np'] = p
    res.append(x)

print('remaining rows', len(res))
c = collections.Counter()
for x in res:
    c['has' if x['np'] else 'none'] += 1
print(c)
json.dump(res, open('AI語譯/_work/review/_g1_np.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for x in res:
    if x['np']:
        print(x['gid'], '||', ' ;; '.join(a + ' => ' + b for a, b in x['np']))
