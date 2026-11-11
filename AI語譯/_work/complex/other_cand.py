# -*- coding: utf-8 -*-
"""Derive candidate fixes for non-live items whose criticized wording persists."""
import json, os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys.path.insert(0, OUT)
from pairs import parse_arrow

QRE = re.compile(r'「([^」]{2,90})」')
def norm(x):
    return re.sub(r'\s+', '', x or '')

BAD_NEW = ('原文', '其餘', '照原', '刪去', '刪除', '待查', '暫不', '不改')

def extract_new(sugg):
    s = (sugg or '').replace('**', '')
    cands = []
    for pat in (r'(?:改為|改作|改成|改回|作)\s*「([^」]{1,120})」',
                r'「[^」]{1,90}」\s*(?:改為|改作|改成|改回)\s*「([^」]{1,120})」'):
        cands += re.findall(pat, s)
    for c in cands:
        c = c.strip()
        if not c or any(b in c for b in BAD_NEW):
            continue
        return c
    return ''

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    other = [r for r in rows if 'OLD_IN_CUR' not in r['flags']]
    out = []
    for i, r in enumerate(other, 1):
        qs = [q for q in QRE.findall(r['problem']) if norm(q) in norm(r['cur'])]
        qs.sort(key=len, reverse=True)
        if not qs or len(qs[0]) < 8:
            continue
        q = qs[0]
        new = extract_new(r['sugg'])
        if not new:
            out.append({'i': i, 'label': r['label'], 'pl': r['pl'], 'q': q, 'new': '', 'sugg': r['sugg'][:90],
                        'cur': r['cur']})
            continue
        old = q
        if new.startswith('（') and '（' in q:
            a = q.find('（'); b = q.rfind('）')
            if b > a:
                old = q[a:b + 1]
        out.append({'i': i, 'label': r['label'], 'pl': r['pl'], 'q': q, 'old': old, 'new': new,
                    'sugg': r['sugg'][:60], 'cur': r['cur']})
    json.dump(out, open(os.path.join(OUT, 'other_cand.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    withnew = [x for x in out if x.get('new')]
    print('candidates', len(out), 'with new', len(withnew))
    lines = []
    for x in out:
        if not x.get('new'):
            continue
        ok = x['cur'].count(x['old'])
        lines.append('%s%d %s|%s|n%d\n  −%s\n  ＋%s' % ('*' if ok != 1 else ' ', x['i'],
                     x['label'].replace('01_行事鈔/', ''), x['pl'], ok, x['old'], x['new']))
    open(os.path.join(OUT, 'other_edits.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('edit lines', len(lines), 'chars', len('\n'.join(lines)))

if __name__ == '__main__':
    main()
