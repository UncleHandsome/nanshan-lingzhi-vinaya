# -*- coding: utf-8 -*-
"""Emit compact old→new review list for live edits (cleaned pairs)."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys.path.insert(0, OUT)
from pairs import parse_arrow

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    live = [r for r in rows if 'OLD_IN_CUR' in r['flags']]
    lines = []
    for i, r in enumerate(live, 1):
        ps = parse_arrow(r['sugg'])
        cur = r['cur']
        if not ps:
            lines.append('!%d %s|%s|%s\n  NO-PAIR %s\n  CUR %s' % (
                i, r['label'].replace('01_行事鈔/', ''), r['pl'], r['conf'], r['sugg'][:120], cur[:150]))
            continue
        for old, new in ps:
            n = cur.count(old)
            lines.append('%s%d %s|%s\n  −%s\n  ＋%s' % (
                '*' if n != 1 or len(new) > len(old) + 12 else ' ', i,
                r['label'].replace('01_行事鈔/', ''), r['pl'],
                old, new if new else '（刪）'))
    p = os.path.join(OUT, 'edit_review.txt')
    open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(p, len(lines))

if __name__ == '__main__':
    main()
