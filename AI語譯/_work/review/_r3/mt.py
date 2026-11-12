# -*- coding: utf-8 -*-
"""mt.py NNN mmmm [mmmm...] -- print 【原文】/【譯文】 of given blocks from 校閱_NNN.txt."""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
nnn = sys.argv[1].zfill(3)
want = sys.argv[2:]
blocks, cur = [], None
for ln in open(os.path.join(MAT, '校閱_%s.txt' % nnn), 'rb').read().decode('utf-8-sig').split('\n'):
    ln = ln.rstrip('\r')
    m = LBL.match(ln)
    if m:
        cur = {'mmmm': m.group(2), 'book': m.group(3), 'chunk': m.group(4), 'src': '', 'tr': ''}
        blocks.append(cur)
        continue
    if cur is None:
        continue
    if ln.startswith('【原文】'):
        cur['src'] = ln[4:]
    elif ln.startswith('【譯文】'):
        cur['tr'] = ln[4:]
for b in blocks:
    if not want or b['mmmm'] in want:
        print('== %s-%s %s/%s' % (nnn, b['mmmm'], b['book'], b['chunk']))
        print('原: ' + b['src'])
        print('譯: ' + b['tr'])
