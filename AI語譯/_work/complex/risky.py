# -*- coding: utf-8 -*-
"""List risky edits for manual verification."""
import json, os, sys, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys.path.insert(0, OUT)
from pairs import parse_arrow

def main():
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    live = [r for r in rows if 'OLD_IN_CUR' in r['flags']]
    lines = []
    for i, r in enumerate(live, 1):
        for old, new in parse_arrow(r['sugg']):
            n = r['cur'].count(old)
            why = []
            if n != 1:
                why.append('occ%d' % n)
            if not new and len(old) <= 3:
                why.append('short-del')
            if new and len(new) > len(old) + 10:
                why.append('long-new')
            if old in ('，', '。', '、', '；'):
                why.append('punct')
            # unbalanced brackets after edit
            ctx = r['cur']
            if new == '':
                j = ctx.find(old)
                left = ctx[max(0, j - 1):j]
                right = ctx[j + len(old):j + len(old) + 1]
                if (left, right) in (('（', '）'), ('「', '」'), ('〔', '〕'), ('《', '》'), ('［', '］')):
                    why.append('unwrap')
                if left in '，、；' and right in '，。；':
                    why.append('dangle')
            if why:
                lines.append('*%d %s|%s|%s [%s]\n  −%s\n  ＋%s\n  CUR %s' % (
                    i, r['label'].replace('01_行事鈔/', ''), r['pl'], r['conf'], ','.join(why),
                    old, new if new else '（刪）',
                    (r['cur'][max(0, r['cur'].find(old) - 60):r['cur'].find(old) + len(old) + 40] if r['cur'].find(old) >= 0 else r['cur'][:100])))
    p = os.path.join(OUT, 'risky.txt')
    open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(p, len(lines), os.path.getsize(p))

if __name__ == '__main__':
    main()
