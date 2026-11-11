# -*- coding: utf-8 -*-
"""Score live-item edits against 原文 support; emit review lists."""
import re, json, os, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys.path.insert(0, OUT)
from triage import parse_arrow, norm

def bigrams(s):
    s = norm(s)
    return set(s[i:i + 2] for i in range(len(s) - 1)) if len(s) > 1 else set(s)

def cov(s, src):
    b = bigrams(s); t = bigrams(src)
    if not b:
        return 1.0
    return len(b & t) / len(b)

def usable_pairs(row):
    pairs = []
    cur = row['cur']
    for old, new in parse_arrow(row['sugg']):
        if old:
            n = cur.count(old)
            if n == 1:
                pairs.append((old, new, 1))
            elif n > 1:
                pairs.append((old, new, n))
        else:
            pairs.append(('', new, 0))
    return pairs

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    live = [r for r in rows if 'OLD_IN_CUR' in r['flags']]
    out = []
    for r in live:
        pairs = usable_pairs(r)
        info = []
        for old, new, n in pairs:
            info.append({'old': old, 'new': new, 'n': n,
                         'old_sup': round(cov(old, r['src']), 2),
                         'new_sup': round(cov(new, r['src']), 2)})
        risky = 0
        for x in info:
            if x['old'] and x['old_sup'] >= 0.55 and x['new_sup'] <= x['old_sup'] + 0.05:
                risky += 1
            if x['n'] > 1:
                risky += 1
        rec = {'label': r['label'], 'pl': r['pl'], 'conf': r['conf'], 'type': r['ptype'],
               'problem': r['problem'], 'basis': r['basis'], 'sugg': r['sugg'], 'cur': r['cur'], 'src': r['src'],
               'pairs': info, 'risky': risky}
        out.append(rec)
    json.dump(out, open(os.path.join(OUT, 'live_edits.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('live', len(out))
    print('risky0', sum(1 for r in out if r['risky'] == 0),
          'risky1+', sum(1 for r in out if r['risky'] >= 1),
          'nopair', sum(1 for r in out if not r['pairs']))
    # stats on support
    hi = sum(1 for r in out if any(x['old'] and x['old_sup'] >= 0.7 for x in r['pairs']))
    print('items whose deleted text is >=0.7 supported by 原文:', hi)

if __name__ == '__main__':
    main()
