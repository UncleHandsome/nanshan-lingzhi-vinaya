# -*- coding: utf-8 -*-
"""edit3.py batch.json -- r3 續跑 (039+) 版本。與 edit2.py 差別：
備份寫到 歸檔/r3修正前/<書>/<chunk>_b.txt（本輪首次改動前的原樣），
不動前一位已建立的 <chunk>.txt。

batch.json = {
 "subs": [ {"nnn":"039","pairs":[["old","new"], ...]}, ... ],
 "log": [ {"nnn":"039","items":25,"fixed":6,"rej":3,"doubt":0,"note":"..."} ]
}
"""
import os, re, sys, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
LOG = os.path.join(WORK, 'fix_r3b.tsv')
DONE = os.path.join(WORK, 'r3_done.tsv')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

def read_txt(p):
    return open(p, 'rb').read().decode('utf-8-sig')

def block_labels(nnn):
    t = read_txt(os.path.join(MAT, '校閱_%s.txt' % nnn))
    seen = []
    for ln in t.split('\n'):
        m = LBL.match(ln.rstrip('\r'))
        if m:
            k = (m.group(3), m.group(4))
            if k not in seen:
                seen.append(k)
    return seen

def main():
    b = json.load(open(sys.argv[1], encoding='utf-8'))
    filecache = {}
    edits = []
    errs = []
    touched = []          # chunks we actually wrote in this run
    for grp in b['subs']:
        nnn = grp['nnn']
        keys = block_labels(nnn)
        pool = []
        for book, chunk in keys:
            if (book, chunk) not in filecache:
                p = os.path.join(OUT, book, chunk + '.txt')
                lines = read_txt(p).split('\n')
                paras = [(i, s.rstrip('\r')) for i, s in enumerate(lines) if s.rstrip('\r').strip()]
                filecache[(book, chunk)] = (lines, paras)
            lines, paras = filecache[(book, chunk)]
            for i, s in paras:
                pool.append((book, chunk, i, s))
        for old, new in grp['pairs']:
            hits = [(bk, ch, i) for bk, ch, i, s in pool if old in s]
            if not hits:
                hits2 = [(bk, ch, i) for bk, ch, i, s in pool if new and new in s]
                if hits2:
                    print('  ALREADY %s: %s' % (nnn, new[:30]))
                else:
                    errs.append((nnn, 'NOTFOUND %r' % old[:60]))
                continue
            if len(hits) > 1:
                errs.append((nnn, 'AMBIG %d %r -> %s' % (
                    len(hits), old[:40],
                    '; '.join('%s/%s#%d' % (x[0], x[1], x[2] + 1) for x in hits[:6]))))
                continue
            bk, ch, i = hits[0]
            lines, paras = filecache[(bk, ch)]
            cur = lines[i].rstrip('\r')
            lines[i] = cur.replace(old, new) + ('\r' if lines[i].endswith('\r') else '')
            pool = [(b2, c2, i2, (lines[i2].rstrip('\r') if (b2, c2) == (bk, ch) else s2))
                    for b2, c2, i2, s2 in pool]
            edits.append((bk, ch, i, old, new))
    bychunk = {}
    for bk, ch, i, old, new in edits:
        bychunk.setdefault((bk, ch), []).append((i, old, new))
    for (bk, ch), items in bychunk.items():
        lines, _ = filecache[(bk, ch)]
        src = os.path.join(OUT, bk, ch + '.txt')
        bp = os.path.join(BAK, bk)
        os.makedirs(bp, exist_ok=True)
        dst = os.path.join(bp, ch + '_b.txt')
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        open(src, 'wb').write('\n'.join(lines).encode('utf-8'))
        touched.append((bk, ch))
        with open(LOG, 'a', encoding='utf-8') as f:
            for i, old, new in items:
                f.write('%s\t%s\t-\t%d\t%s\t<<%s\n' % (bk, ch, i + 1, old[:40], lines[i].rstrip('\r')[:40]))
        print('WROTE %s/%s  %d subs' % (bk, ch, len(items)))
    print('TOTAL SUBS', len(edits))
    if errs:
        print('--- ERRORS %d ---' % len(errs))
        for n, m in errs:
            print(n, '|', m)
    if b.get('log'):
        with open(DONE, 'a', encoding='utf-8') as f:
            for r in b['log']:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (r['nnn'], r['items'], r['fixed'],
                                                      r['rej'], r['doubt'], r.get('note', '')))
        print('LOGGED', len(b['log']))

main()
