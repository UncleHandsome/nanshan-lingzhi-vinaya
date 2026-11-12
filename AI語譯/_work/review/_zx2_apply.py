# -*- coding: utf-8 -*-
"""r2 1048-1180 套用器（備份 _m3）。
用法: python _zx2_apply.py edits_1048.json [--dry] [--done]
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

BKM3 = os.path.join(L.ROOT, '歸檔', 'r2修正前', '資持記')
LOGD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_zx2_log')


def backup_m3(book, chunk, src):
    d = BKM3 if book == '資持記' else os.path.join(BKM3, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_m3.txt')
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    return dst


def main():
    path = sys.argv[1]
    dry = '--dry' in sys.argv
    done = '--done' in sys.argv
    d = json.load(open(path, encoding='utf-8-sig'))
    n = int(d['n'])
    edits = d.get('edits', [])
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
            if t2.count('\n') + t2.count('\r') != nl0:
                raise SystemExit('NEWLINE CHANGED %s#%d' % (chunk, e['seg']))
            segs[i] = t2
            logs.append(dict(book=book, chunk=chunk, seg=e['seg'], old=e['old'], new=e['new'], why=e.get('why', '')))
        if len(segs) != len(o.segs):
            raise SystemExit('SEGCOUNT')
        if not dry:
            backup_m3(book, chunk, o.path)
            o.segs = segs
            o.save()
        print('%s %s/%s: %d edits' % ('DRY' if dry else 'OK', book, chunk, len(es)))
    if not dry:
        os.makedirs(LOGD, exist_ok=True)
        with open(os.path.join(LOGD, 'log_%d.json' % n), 'w', encoding='utf-8') as f:
            json.dump(dict(n=n, edits=logs, verdicts=d.get('verdicts', [])), f, ensure_ascii=False, indent=1)
        if done:
            L.append_done(n)
    print('applied %d edits for %d%s' % (len(logs), n, ' (dry)' if dry else ''))


if __name__ == '__main__':
    main()
