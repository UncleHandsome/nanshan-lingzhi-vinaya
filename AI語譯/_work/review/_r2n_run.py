# -*- coding: utf-8 -*-
"""r2 1801-1870: apply edits with _n4 backup + log + r2_done.
usage: python _r2n_run.py specs_1801_1803.json [--dry] [--no-done]
specs json: [{"n":1801,"items":[[seq,old,new,why],...],"verdicts":[...]}, ...]
"""
import os, sys, json, shutil, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L
import _r2d_build as B

BK = os.path.join(L.ROOT, '歸檔', 'r2修正前')
LOGD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log')
SUF = '_n4.txt'


def backup4(book, chunk, src):
    d = os.path.join(BK, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + SUF)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    return dst


def apply_one(n, edits, verdicts, dry=False, done=True):
    by = {}
    for e in edits:
        by.setdefault((e['book'], e['chunk']), []).append(e)
    logs = []
    for (book, chunk), es in by.items():
        o = L.Out(book, chunk)
        segs = list(o.segs)
        for e in es:
            i = e['seg'] - 1
            if not (0 <= i < len(segs)):
                raise SystemExit('SEG RANGE %s#%d (n=%d)' % (chunk, e['seg'], len(segs)))
            t = segs[i]
            c = t.count(e['old'])
            if c != 1:
                raise SystemExit('COUNT %d %s/%s#%d old=%r' % (c, book, chunk, e['seg'], e['old'][:100]))
            nl0 = t.count('\n') + t.count('\r')
            t2 = t.replace(e['old'], e['new'])
            if t2 == t:
                raise SystemExit('NOCHANGE %s#%d' % (chunk, e['seg']))
            if t2.count('\n') + t2.count('\r') != nl0:
                raise SystemExit('NEWLINE CHANGED %s#%d' % (chunk, e['seg']))
            segs[i] = t2
            logs.append(dict(book=book, chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e.get('why', '')))
        if len(segs) != len(o.segs):
            raise SystemExit('SEGCOUNT')
        if not dry:
            backup4(book, chunk, o.path)
            o.segs = segs
            o.save()
    if not dry:
        os.makedirs(LOGD, exist_ok=True)
        with open(os.path.join(LOGD, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
            json.dump(dict(n=n, edits=logs, verdicts=verdicts), f, ensure_ascii=False, indent=1)
        if done:
            L.append_done(n)
    print('%s %d: %d edits, %d segs, %d verdicts' % ('DRY' if dry else 'OK', n, len(logs), len(set(e['seg'] for e in logs)), len(verdicts)))


def main():
    path = sys.argv[1]
    dry = '--dry' in sys.argv
    done = '--no-done' not in sys.argv
    specs = json.load(open(path, encoding='utf-8-sig'))
    for sp in specs:
        n = int(sp['n'])
        items = [tuple(x) for x in sp['items']]
        B.make(n, items, sp.get('verdicts', []), quiet=True)
        d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edits_%d.json' % n), encoding='utf-8'))
        apply_one(n, d['edits'], d.get('verdicts', []), dry=dry, done=done)


if __name__ == '__main__':
    main()
