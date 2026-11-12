# -*- coding: utf-8 -*-
"""套用：吃 JSON 清單 [{n, edits:[{book,chunk,seg,old,new,why}]}]，
每批先驗相似度（ratio>=0.94 或已定位），套用時硬條件 old 只出現一次。
用法: python _zx1342_apply.py _zx1342_e/1342.json [...] [--dry]
"""
import os, sys, json, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _zx1342_lib as L

LOGD = os.path.join(os.path.dirname(__file__), '_zx1342_log')


def check_align(n):
    bad = []
    for r in L.parse_review(n):
        seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
        if ratio < 0.94:
            bad.append((r['seq'], r['seg'], seg, round(ratio, 3)))
    return bad


def main():
    paths = [a for a in sys.argv[1:] if a.endswith('.json')]
    dry = '--dry' in sys.argv
    os.makedirs(LOGD, exist_ok=True)
    total = 0
    for p in paths:
        d = json.load(open(p, encoding='utf-8-sig'))
        n = d['n']
        bad = check_align(n)
        if bad and not d.get('force'):
            print('ALIGN FAIL %d %s' % (n, bad))
            raise SystemExit('stop')
        if bad:
            print('ALIGN WARN %d %s (force)' % (n, bad))
        by = {}
        for e in d['edits']:
            by.setdefault((e['book'], e['chunk']), []).append(e)
        res = []
        for (book, chunk), es in by.items():
            r = L.apply_batch(book, chunk, es, dry=dry)
            res.append(r)
            print('%s %d %s/%s n=%d changed=%s' % (
                'DRY' if dry else 'OK', n, book, chunk, r['n'], r['changed']))
        total += len(d['edits'])
        if not dry:
            json.dump(dict(n=n, chunks=res, verdicts=d.get('verdicts', [])),
                      open(os.path.join(LOGD, 'log_%d.json' % n), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            L.append_done(str(n))
    print('TOTAL edits=%d' % total)


if __name__ == '__main__':
    main()
