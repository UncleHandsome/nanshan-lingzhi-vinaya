# -*- coding: utf-8 -*-
"""工作單：印出 resp 全文 + 只印被引用的段（原文＋現行譯文）。用法: python _zx1031_ws.py 1032 [1033 ...]"""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

RESP = os.path.join(L.ROOT, 'batch_qwen', 'r2')


def cited_seqs(txt):
    s = set()
    for m in re.finditer(r'[【\[\(（]#?(\d{3,4})[】\]\)）]', txt):
        v = int(m.group(1))
        if 1 <= v <= 99:
            s.add(v)
    for m in re.finditer(r'^#{2,4}\s*#?(\d{3,4})\s*$', txt, re.M):
        v = int(m.group(1))
        if 1 <= v <= 99:
            s.add(v)
    for m in re.finditer(r'段\s*(\d{1,2})\b', txt):
        v = int(m.group(1))
        if 1 <= v <= 99:
            s.add(v)
    return s


def main():
    for a in sys.argv[1:]:
        n = int(a)
        rp = os.path.join(RESP, 'resp_%d.txt' % n)
        print('########## resp_%d ##########' % n)
        if not os.path.exists(rp):
            print('<<<RESP MISSING>>>')
            continue
        txt = open(rp, encoding='utf-8').read()
        print(txt.rstrip())
        recs = L.parse_review(n)
        by = {r['seq']: r for r in recs}
        want = cited_seqs(txt)
        want = set(want) | {1} if want else set(by)
        miss = [s for s in want if s not in by]
        cache = {}
        print('\n----- 段（僅被引用者） -----')
        for seq in sorted(want):
            if seq not in by:
                continue
            r = by[seq]
            key = (r['book'], r['chunk'])
            if key not in cache:
                cache[key] = L.Out(*key)
            o = cache[key]
            cur = o.segs[r['seg'] - 1]
            mark = ' [MAT!=CUR]' if cur.replace('\n', '') != (r['trans'] or '').replace('\n', '') else ''
            print('=== %d-%04d %s/%s#%d%s' % (r['batch'], r['seq'], r['book'], r['chunk'], r['seg'], mark))
            print('原: ' + (r['orig'] or ''))
            print('譯: ' + cur)
        if miss:
            print('(cited but absent: %s)' % miss, file=sys.stderr)
        print()


if __name__ == '__main__':
    main()
