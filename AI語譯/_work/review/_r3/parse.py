# -*- coding: utf-8 -*-
"""Parse 校閱_10K/校閱_NNN.txt blocks and align to AI語譯/out/<book>/<chunk>.txt paragraphs."""
import os, re, json, sys, io
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(ROOT, '校閱_10K')
OUT = os.path.join(ROOT, 'AI語譯', 'out')

LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')

def read(p):
    b = open(p, 'rb').read()
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n')
    t = b.decode('utf-8-sig')
    return t, crlf, lf, ('CRLF' if crlf and crlf == lf else ('LF' if crlf == 0 else 'MIXED'))

def parse_mat(nnn):
    p = os.path.join(MAT, '校閱_%s.txt' % nnn)
    t, crlf, lf, eol = read(p)
    lines = t.split('\n')
    blocks = []
    cur = None
    for ln in lines:
        ln = ln.rstrip('\r')
        m = LBL.match(ln)
        if m:
            cur = {'nnn': m.group(1), 'mmmm': m.group(2), 'book': m.group(3),
                   'chunk': m.group(4), 'seg': int(m.group(5)), 'src': None, 'tr': None}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        if ln.startswith('【原文】'):
            cur['src'] = ln[len('【原文】'):]
        elif ln.startswith('【譯文】'):
            cur['tr'] = ln[len('【譯文】'):]
    return blocks, eol

def out_paras(book, chunk):
    p = os.path.join(OUT, book, chunk + '.txt')
    t, crlf, lf, eol = read(p)
    lines = t.split('\n')
    paras = []          # (line_index, text)
    for i, ln in enumerate(lines):
        s = ln.rstrip('\r')
        if s.strip():
            paras.append((i, s))
    return paras, eol, lines

def main():
    nnns = sorted(set(re.match(r'resp_(\d{3})\.txt', f).group(1)
                      for f in os.listdir(os.path.join(ROOT, 'batch_qwen', 'r3'))
                      if re.match(r'resp_(\d{3})\.txt', f)))
    allrows = []
    for nnn in nnns:
        blocks, eol = parse_mat(nnn)
        for b in blocks:
            allrows.append(b)
    # align
    cache = {}
    ok = bad = 0
    for b in allrows:
        key = (b['book'], b['chunk'])
        if key not in cache:
            cache[key] = out_paras(*key)
        paras, oel, lines = cache[key]
        idx = b['seg'] - 1
        b['ok'] = False
        if 0 <= idx < len(paras):
            li, txt = paras[idx]
            b['line'] = li
            b['cur'] = txt
            if b['tr'] is not None and txt.strip() == b['tr'].strip():
                b['ok'] = True
        if b['ok']:
            ok += 1
        else:
            bad += 1
    print('blocks', len(allrows), 'ok', ok, 'bad', bad)
    for b in allrows:
        if not b['ok']:
            print('BAD', b['nnn'], b['mmmm'], b['book'], b['chunk'], b['seg'],
                  '| cur:', (b.get('cur') or '')[:60], '| mat:', (b['tr'] or '')[:60])
    json.dump(allrows, open(os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r3', 'blocks.json'), 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=0)

main()
