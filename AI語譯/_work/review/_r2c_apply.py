# -*- coding: utf-8 -*-
"""批次套用 TSV（_r2c 版，_k 備份）。
### 1491
@@ -
seq<TAB>old<TAB>new
用法: python _r2c_apply.py _r2c_edits.txt [--dry]
"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L
import _r2c_lib as B


def norm(s):
    return ''.join(ch for ch in (s or '') if ch not in ' \t\r\n')


def align_ok(n):
    bad = []
    for r in L.parse_review(n):
        o = L.Out(r['book'], r['chunk'])
        if r['seg'] - 1 >= len(o.segs):
            bad.append((r['seq'], r['seg'], 0.0, 'range'))
            continue
        rt = difflib.SequenceMatcher(None, norm(r['trans']), norm(o.segs[r['seg'] - 1])).ratio()
        if rt < 0.94:
            bad.append((r['seq'], r['seg'], round(rt, 3), 'need_locate'))
    return bad


def parse(path):
    blocks = {}
    n = None
    book = chunk = None
    for ln in open(path, encoding='utf-8-sig'):
        ln = ln.rstrip('\n').rstrip('\r')
        if not ln.strip():
            continue
        if ln.startswith('### '):
            n = int(ln[4:].strip())
            blocks[n] = []
            book = chunk = None
            continue
        if ln.startswith('@@ '):
            v = ln[3:].strip()
            if v == '-':
                book, chunk = '-', '-'
            else:
                book, chunk = v.split('/')
            continue
        parts = ln.split('\t')
        if len(parts) != 3:
            raise SystemExit('BAD LINE %r' % ln[:80])
        seg, old, new = parts
        blocks[n].append(dict(book=book, chunk=chunk, seg=int(seg), old=old, new=new))
    return blocks


def main():
    path = sys.argv[1]
    dry = '--dry' in sys.argv
    only = None
    for a in sys.argv[2:]:
        if a.isdigit():
            only = int(a)
    blocks = parse(path)
    for n in list(blocks):
        recs = {r['seq']: r for r in L.parse_review(n)}
        for e in blocks[n]:
            if e['book'] == '-':
                r = recs.get(e['seg'])
                if not r:
                    raise SystemExit('NO SEQ %d-%d' % (n, e['seg']))
                e['book'] = r['book']; e['chunk'] = r['chunk']; e['seg'] = r['seg']
    for n in sorted(blocks):
        if only and n != only:
            continue
        bad = align_ok(n)
        if bad:
            print('ALIGN FAIL %d %s' % (n, bad))
            raise SystemExit('stop at %d' % n)
        print('-- %d: align ok, %d edits' % (n, len(blocks[n])))
        B.run(n, blocks[n], [], dry=dry)


if __name__ == '__main__':
    main()
