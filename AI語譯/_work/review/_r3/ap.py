# -*- coding: utf-8 -*-
"""ap.py NNN pairs.txt -- apply phrase substitutions for one 校閱 file + log.

pairs.txt format (UTF-8):
  #items=11 fixed=7 rej=3 doubt=1 note=...
  old<TAB>new
  old<TAB>new
Routing: unique paragraph among 校閱_NNN's chunks containing `old`. NOTFOUND/AMBIG reported.
Backup 歸檔/r3修正前/<book>/<chunk>.txt (first time). Line endings preserved.
"""
import os, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
BAK = os.path.join(ROOT, '歸檔', 'r3修正前')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review')
LOG = os.path.join(WORK, 'fix_r3.tsv')
DONE = os.path.join(WORK, 'r3_done.tsv')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

def read_txt(p):
    return open(p, 'rb').read().decode('utf-8-sig')

def block_labels(nnn):
    seen = []
    for ln in read_txt(os.path.join(MAT, '校閱_%s.txt' % nnn)).split('\n'):
        m = LBL.match(ln.rstrip('\r'))
        if m:
            k = (m.group(3), m.group(4))
            if k not in seen:
                seen.append(k)
    return seen

def main():
    nnn = sys.argv[1].zfill(3)
    pl = sys.argv[2]
    hdr, pairs = None, []
    for ln in open(pl, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.startswith('#'):
            if ln.startswith('#items='):
                hdr = ln[1:]
            continue
        old, new = ln.split('\t')
        pairs.append((old, new))
    keys = block_labels(nnn)
    filecache, pool = {}, []
    for book, chunk in keys:
        if (book, chunk) not in filecache:
            lines = read_txt(os.path.join(OUT, book, chunk + '.txt')).split('\n')
            paras = [(i, s.rstrip('\r')) for i, s in enumerate(lines) if s.rstrip('\r').strip()]
            filecache[(book, chunk)] = [lines, paras]
        lines, paras = filecache[(book, chunk)]
        for i, s in paras:
            pool.append((book, chunk, i, s))
    edits, errs = [], []
    for old, new in pairs:
        hits = [(bk, ch, i) for bk, ch, i, s in pool if old in s]
        if not hits:
            hits2 = [(bk, ch, i) for bk, ch, i, s in pool if new and new in s]
            if hits2:
                print('  ALREADY %s: %s' % (nnn, new[:28]))
            else:
                errs.append((nnn, 'NOTFOUND %r' % old[:50]))
            continue
        if len(hits) > 1:
            errs.append((nnn, 'AMBIG %d %r' % (len(hits), old[:40])))
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
        dst = os.path.join(bp, ch + '.txt')
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        open(src, 'wb').write('\n'.join(lines).encode('utf-8'))
        with open(LOG, 'a', encoding='utf-8') as f:
            for i, old, new in items:
                f.write('%s\t%s\t-\t%d\t%s\t<<%s\n' % (bk, ch, i + 1, lines[i].rstrip('\r'), old[:20]))
        print('WROTE %s/%s  %d subs' % (bk, ch, len(items)))
    print('TOTAL %s SUBS %d' % (nnn, len(edits)))
    if errs:
        print('--- ERRORS %d ---' % len(errs))
        for n, m in errs:
            print(n, '|', m)
    if hdr:
        kv = dict(x.split('=', 1) for x in hdr.split('|'))
        with open(DONE, 'a', encoding='utf-8') as f:
            f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (nnn, kv['items'], kv['fixed'],
                                                  kv['rej'], kv['doubt'], kv.get('note', '')))

main()
