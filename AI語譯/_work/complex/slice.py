# -*- coding: utf-8 -*-
"""Split slim card file into per-slice files by blank-line separated items."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')

def split_file(name, n):
    p = os.path.join(OUT, 'slim_%s.txt' % name)
    txt = open(p, encoding='utf-8').read()
    items = [x.strip('\n') for x in txt.split('\n\n') if x.strip()]
    d = os.path.join(OUT, 'slice_%s' % name)
    os.makedirs(d, exist_ok=True)
    for i in range(0, len(items), n):
        chunk = items[i:i + n]
        fn = os.path.join(d, '%02d.txt' % (i // n + 1))
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(chunk) + '\n')
    ids = [[it.split(']')[0].lstrip('[') for it in items[i:i + n]][0] + '-' + [it.split(']')[0].lstrip('[') for it in items[i:i + n]][-1] for i in range(0, len(items), n)]
    print(name, 'items', len(items), 'slices', (len(items) + n - 1) // n)
    print(' '.join(ids))

if __name__ == '__main__':
    split_file('live', int(sys.argv[1]) if len(sys.argv) > 1 else 65)
    split_file('other', int(sys.argv[2]) if len(sys.argv) > 2 else 65)
