# -*- coding: utf-8 -*-
"""重建本輪（1572-1583）改動前狀態為 _l2 備份：由現行 out 反向套用 log 的 new->old。"""
import os, sys, json, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

LOGD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log')
BK = os.path.join(L.ROOT, '歸檔', 'r2修正前')
chunks = {}
for n in range(1572, 1584):
    p = os.path.join(LOGD, 'log_%d.json' % n)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    for e in d['edits']:
        chunks.setdefault((e['book'], e['chunk']), []).append(e)

for (book, chunk), es in chunks.items():
    o = L.Out(book, chunk)
    segs = list(o.segs)
    bad = 0
    for e in reversed(es):
        t = segs[e['seg'] - 1]
        c = t.count(e['new'])
        if c != 1:
            bad += 1
            print('!! reverse count=%d %s/%s#%d new=%r' % (c, book, chunk, e['seg'], e['new'][:40]))
            continue
        segs[e['seg'] - 1] = t.replace(e['new'], e['old'])
    d = os.path.join(BK, book)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, chunk + '_l2.txt')
    if os.path.exists(dst):
        print('SKIP exists', dst)
        continue
    new = (o.eol + o.eol).join(segs) + o.trailing
    open(dst, 'wb').write(new.encode('utf-8'))
    print('OK %s/%s -> %s (%d edits reversed, bad=%d, segs=%d)' % (book, chunk, os.path.basename(dst), len(es), bad, len(segs)))

# 02b: _l 是本輪首次改動前建立，複製為 _l2
src = os.path.join(BK, '03_業疏', '02b_卷一之二_l.txt')
dst = os.path.join(BK, '03_業疏', '02b_卷一之二_l2.txt')
if os.path.exists(src) and not os.path.exists(dst):
    import shutil
    shutil.copy2(src, dst)
    print('OK copy 02b _l -> _l2')
