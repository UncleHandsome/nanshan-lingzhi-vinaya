# -*- coding: utf-8 -*-
"""Dump selected paragraphs: python tmp_seg.py <file> <seg> [seg...]"""
import sys, io, re

t = io.open(sys.argv[1], encoding='utf-8').read()
ps = [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]
for a in sys.argv[2:]:
    i = int(a) - 1
    print('=== seg %d ===' % (i + 1))
    print(ps[i])
    print('')
