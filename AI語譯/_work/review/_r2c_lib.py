# -*- coding: utf-8 -*-
"""r2 1491-1648 套用工具（_k 備份、逐段套用、驗證、log、done）。"""
import os, re, json, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import _r2a_lib as L

BK = os.path.join(L.ROOT, '歸檔', 'r2修正前')
LOGD = os.path.join(os.path.dirname(__file__), '_r2c_log')


def backup_k(book, chunk, src):
    d = os.path.join(BK, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_k.txt')
    if os.path.exists(dst):
        return dst, False
    shutil.copy2(src, dst)
    return dst, True


def apply_batch(book, chunk, edits, dry=False):
    o = L.Out(book, chunk)
    segs = list(o.segs)
    before = list(segs)
    by = {}
    for e in edits:
        by.setdefault(e['seg'], []).append(e)
    for segno, es in sorted(by.items()):
        i = segno - 1
        if not (0 <= i < len(segs)):
            raise SystemExit('SEG RANGE %s#%d (n=%d)' % (chunk, segno, len(segs)))
        t = segs[i]
        for e in es:
            c = t.count(e['old'])
            if c != 1:
                import difflib
                sm = difflib.SequenceMatcher(None, t, e['old'])
                m = sm.find_longest_match(0, len(t), 0, len(e['old']))
                ctx = t[max(0, m.a - 70):m.a + m.size + 70]
                raise SystemExit('COUNT %d %s/%s#%d old=%r matchlen=%d ctx=%s' % (
                    c, book, chunk, segno, e['old'][:60], m.size, ctx))
            t = t.replace(e['old'], e['new'])
        segs[i] = t
        if '\n' in t or '\r' in t:
            raise SystemExit('NEWLINE seg %s#%d' % (chunk, segno))
    if len(segs) != len(before):
        raise SystemExit('SEGCOUNT')
    if not dry:
        dst, created = backup_k(book, chunk, o.path)
        o.segs = segs
        o.save()
        return dict(book=book, chunk=chunk, backup=dst, created=created,
                    n=len(segs), eol=repr(o.eol),
                    changed=[i + 1 for i in range(len(segs)) if segs[i] != before[i]],
                    edits=edits)
    return dict(book=book, chunk=chunk, dry=True, n=len(segs), eol=repr(o.eol),
                changed=[i + 1 for i in range(len(segs)) if segs[i] != before[i]], edits=edits)


def run(n, edits, verdicts, dry=False):
    by = {}
    for e in edits:
        by.setdefault((e['book'], e['chunk']), []).append(e)
    res = []
    for (book, chunk), es in by.items():
        r = apply_batch(book, chunk, es, dry=dry)
        res.append(r)
        print('%s %s/%s seg=%d eol=%s changed=%s' % ('DRY' if dry else 'OK', book, chunk,
                                                     r['n'], r['eol'], r['changed']))
    if not dry:
        os.makedirs(LOGD, exist_ok=True)
        json.dump(dict(n=n, chunks=res, verdicts=verdicts),
                  open(os.path.join(LOGD, 'log_%d.json' % n), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        L.append_done(n)
    return res
