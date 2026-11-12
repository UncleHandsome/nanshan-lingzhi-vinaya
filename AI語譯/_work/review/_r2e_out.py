# -*- coding: utf-8 -*-
"""印 out 指定段：python _r2e_out.py 09a 30-34 [09b 1-5]
參數：chunk 名（可含書別 03_業疏/09a）＋段號或段號範圍。"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L


def main():
    a = sys.argv[1:]
    i = 0
    while i < len(a):
        chunk = a[i]
        book = '03_業疏'
        if '/' in chunk:
            book, chunk = chunk.split('/', 1)
        i += 1
        spec = a[i] if i < len(a) else ''
        i += 1
        if '-' in spec:
            s, e = spec.split('-', 1)
            rng = range(int(s), int(e) + 1)
        else:
            rng = [int(spec)] if spec else []
        o = L.Out(book, chunk)
        for s in rng:
            if 1 <= s <= len(o.segs):
                print('=== %s/%s#%d' % (book, chunk, s))
                print(o.segs[s - 1])
                print()


if __name__ == '__main__':
    main()
