# -*- coding: utf-8 -*-
"""seg.py NNN [MMMM ...]  -- print material block(s) with CURRENT out text."""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(ROOT, 'AI語譯', 'out')
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

def read(p):
    b = open(p, 'rb').read()
    t = b.decode('utf-8-sig')
    crlf, lf = b.count(b'\r\n'), b.count(b'\n')
    eol = 'CRLF' if crlf and crlf == lf else ('LF' if crlf == 0 else 'MIXED')
    return t, eol

def parse_mat(nnn):
    t, _ = read(os.path.join(MAT, '校閱_%s.txt' % nnn))
    blocks, cur = [], None
    for ln in t.split('\n'):
        ln = ln.rstrip('\r')
        m = LBL.match(ln)
        if m:
            cur = {'label': m.group(1) + '-' + m.group(2), 'book': m.group(3),
                   'chunk': m.group(4), 'src': '', 'tr': ''}
            blocks.append(cur); continue
        if cur is None: continue
        if ln.startswith('【原文】'): cur['src'] = ln[4:]
        elif ln.startswith('【譯文】'): cur['tr'] = ln[4:]
    return blocks

def out_paras(book, chunk):
    t, eol = read(os.path.join(OUT, book, chunk + '.txt'))
    lines = t.split('\n')
    paras = [(i, s.rstrip('\r')) for i, s in enumerate(lines) if s.rstrip('\r').strip()]
    return paras, eol

def main():
    args = sys.argv[1:]
    only_tr = False
    if args and args[0] in ('-t', '--tr'):
        only_tr = True
        args = args[1:]
    nnn = args[0].zfill(3)
    want = [w.zfill(4) for w in args[1:]]
    blocks = parse_mat(nnn)
    cache = {}
    for b in blocks:
        if want and b['label'].split('-')[1] not in want:
            continue
        key = (b['book'], b['chunk'])
        if key not in cache:
            cache[key] = out_paras(*key)[0]
        paras = cache[key]
        # locate: exact unique, else fuzzy best
        cur = None; pi = None
        exact = [i for i, (li, s) in enumerate(paras) if s.strip() == b['tr'].strip()]
        if len(exact) == 1:
            pi = exact[0]; cur = paras[pi][1]
        else:
            import difflib
            best = (-1, 0.0)
            for i, (li, s) in enumerate(paras):
                r = difflib.SequenceMatcher(None, s, b['tr']).ratio()
                if r > best[1]: best = (i, r)
            if best[1] > 0.6:
                pi = best[0]; cur = paras[pi][1]
        print('=' * 5, b['label'], '%s/%s' % (b['book'], b['chunk']),
              'out#%s' % (pi + 1 if pi is not None else '?'),
              '(DIFF tr=%d)' % len(b['tr']))
        if not only_tr:
            print('[原]', b['src'])
        print('[譯]', cur if cur is not None else b['tr'])
        if cur is not None and cur.strip() != b['tr'].strip() and not only_tr:
            print('[材料譯文不同]', b['tr'])

main()
