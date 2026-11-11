# -*- coding: utf-8 -*-
"""Align material blocks to current out paragraphs by fuzzy content matching."""
import os, re, sys, json, difflib
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
    t, eol = read(os.path.join(MAT, '校閱_%s.txt' % nnn))
    blocks, cur = [], None
    for ln in t.split('\n'):
        ln = ln.rstrip('\r')
        m = LBL.match(ln)
        if m:
            cur = {'nnn': m.group(1), 'mmmm': m.group(2), 'book': m.group(3),
                   'chunk': m.group(4), 'seg': int(m.group(5)), 'src': '', 'tr': ''}
            blocks.append(cur); continue
        if cur is None: continue
        if ln.startswith('【原文】'): cur['src'] = ln[4:]
        elif ln.startswith('【譯文】'): cur['tr'] = ln[4:]
    return blocks, eol

def out_paras(book, chunk):
    t, eol = read(os.path.join(OUT, book, chunk + '.txt'))
    lines = t.split('\n')
    paras = [(i, s.rstrip('\r')) for i, s in enumerate(lines) if s.rstrip('\r').strip()]
    return paras, eol, lines

def build():
    nnns = sorted(set(re.match(r'resp_(\d{3})\.txt', f).group(1)
                      for f in os.listdir(os.path.join(ROOT, 'batch_qwen', 'r3'))
                      if re.match(r'resp_(\d{3})\.txt', f)))
    rows = []
    for n in nnns:
        b, _ = parse_mat(n)
        rows.extend(b)
    # group by book/chunk
    cache, res = {}, []
    for b in rows:
        key = (b['book'], b['chunk'])
        if key not in cache:
            cache[key] = out_paras(*key)
        paras, oel, lines = cache[key]
        b['oel'] = oel
        n = len(paras)
        exact = [i for i, (li, s) in enumerate(paras) if s.strip() == b['tr'].strip()]
        if len(exact) == 1:
            b['pi'] = exact[0]; b['ratio'] = 1.0; b['how'] = 'exact'
            res.append(b); continue
        # fuzzy: prefer near label
        best = (-1, 0.0)
        for i, (li, s) in enumerate(paras):
            r = difflib.SequenceMatcher(None, s, b['tr']).quick_ratio()
            if r < 0.55: continue
            r = difflib.SequenceMatcher(None, s, b['tr']).ratio()
            if r > best[1]:
                best = (i, r)
        b['pi'] = best[0]; b['ratio'] = round(best[1], 3); b['how'] = 'fuzzy'
        res.append(b)
    json.dump(res, open(os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r3', 'blocks.json'),
                        'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    bad = [b for b in res if b['ratio'] < 0.999]
    print('total', len(res), 'exact', sum(1 for b in res if b['how'] == 'exact'), 'fuzzy', len(bad))
    for b in bad:
        print('%s-%s %s/%s lbl#%d -> out#%d r=%.3f' % (b['nnn'], b['mmmm'], b['book'], b['chunk'],
              b['seg'], b['pi'] + 1, b['ratio']))

if __name__ == '__main__':
    build()
