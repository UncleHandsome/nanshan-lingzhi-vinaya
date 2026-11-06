# -*- coding: utf-8 -*-
"""Dump source+translation paragraphs for given segs.

python tmp_pair.py <book> <chunk> <seg> [seg...]
"""
import sys, io, re

SRCDIR = {'01_行事鈔': '01_行事鈔', '02_戒疏': '02_戒疏',
          '04_比丘尼鈔': '04_比丘尼鈔', '05_拾毗尼義鈔': '05_拾毗尼義鈔',
          '資持記': '資持記_細分'}

def paras_all(path):
    t = io.open(path, encoding='utf-8').read()
    return [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]

def src_paras(path):
    t = io.open(path, encoding='utf-8').read()
    lines = t.split('\n')
    body = lines[5:]
    return [x for x in body if x.strip()]

book, chunk = sys.argv[1], sys.argv[2]
out = io.open(sys.argv[3], 'w', encoding='utf-8')
tr = paras_all('AI語譯/out/%s/%s.txt' % (book, chunk))
sr = src_paras('TXT_分卷/%s/%s.txt' % (SRCDIR[book], chunk))
out.write('TR paras=%d  SRC paras=%d\n' % (len(tr), len(sr)))
for a in sys.argv[4:]:
    i = int(a) - 1
    out.write('\n######## seg %d ########\n' % (i + 1))
    out.write('--- SRC ---\n')
    out.write((sr[i] if 0 <= i < len(sr) else '<OUT OF RANGE>') + '\n')
    out.write('--- TR ---\n')
    out.write((tr[i] if 0 <= i < len(tr) else '<OUT OF RANGE>') + '\n')
out.close()
print('written')
