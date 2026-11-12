# -*- coding: utf-8 -*-
"""依材料 seq 自動解析 book/chunk/seg，產生 edits json。
用法（於 per-file 腳本）：
    import _zx1031_build as B
    B.make(1031, [(7, old, new, why), ...], [dict(seq=..,kind=..,reason=..), ...])
同一 seq 可多筆。seg 由材料標籤取得，避免 seq/seg 混淆。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))


def segmap(n):
    return {r['seq']: (r['book'], r['chunk'], r['seg']) for r in L.parse_review(n)}, len(L.parse_review(n))


def make(n, items, verdicts=None, quiet=False):
    m, total = segmap(n)
    E = []
    cache = {}
    for seq, old, new, why in items:
        if seq not in m:
            raise SystemExit('BAD SEQ %r for %d' % (seq, n))
        book, chunk, seg = m[seq]
        key = (book, chunk)
        if key not in cache:
            cache[key] = L.Out(book, chunk)
        t = cache[key].segs[seg - 1]
        c = t.count(old)
        if c != 1:
            where = [(s, k) for k, (b, ch, s) in m.items() if old in cache[key].segs[s - 1]] if key == (book, chunk) else []
            print('!! %d seq%d seg%d count=%d old=%r  出現於seq:%s' % (n, seq, seg, c, old[:60], where))
        E.append(dict(book=book, chunk=chunk, seg=seg, old=old, new=new, why=why, seq=seq))
    for x in E:
        x.pop('seq', None)
    path = os.path.join(HERE, 'edits_%d.json' % n)
    json.dump(dict(n=n, segs=total, edits=E, verdicts=verdicts or []),
              open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if not quiet:
        print('%d: %d edits, %d verdicts, %d segs -> %s' % (n, len(E), len(verdicts or []), total, os.path.basename(path)))
    return path
