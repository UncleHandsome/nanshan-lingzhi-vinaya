# -*- coding: utf-8 -*-
"""edit4.py batch.json [--show] -- r3c (061-180) 續跑版。

差別於 edit3.py：
 - 備份寫 歸檔/r3修正前/<書>/<chunk>_c.txt（本輪首次改動前的原樣）
 - 明細寫 fix_r3c.tsv
 - --show 印出改動後的整段（截 160 字）以便目視
batch.json = {
 "subs": [ {"nnn":"061","pairs":[["old","new"], ...]}, ... ],
 "log": [ {"nnn":"061","items":13,"fixed":6,"rej":5,"doubt":2,"note":"..."} ]
}
"""
import os, re, sys, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
LOG = os.path.join(WORK, 'fix_r3c.tsv')
DONE = os.path.join(WORK, 'r3_done.tsv')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
SHOW = '--show' in sys.argv

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
    b = json.load(open(sys.argv[1], encoding='utf-8-sig'))
    filecache, edits, errs = {}, [], []
    for grp in b['subs']:
        nnn = grp['nnn']
        pool = []
        for book, chunk in block_labels(nnn):
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
            newline = cur.replace(old, new)
            if newline == cur:
                errs.append((nnn, 'NOCHANGE %r' % old[:40]))
                continue
            lines[i] = newline + ('\r' if lines[i].endswith('\r') else '')
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
        dst = os.path.join(bp, ch + '_c.txt')
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        open(src, 'wb').write('\n'.join(lines).encode('utf-8'))
        with open(LOG, 'a', encoding='utf-8') as f:
            for i, old, new in items:
                f.write('%s\t%s\t-\t%d\t%s\t<<%s\n' % (bk, ch, i + 1, old[:40], lines[i].rstrip('\r')[:60]))
        print('WROTE %s/%s  %d subs' % (bk, ch, len(items)))
        if SHOW:
            for i in sorted(set(i for i, _, _ in items)):
                print('   #%d %s' % (i + 1, lines[i].rstrip('\r')[:170]))
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
