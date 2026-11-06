# -*- coding: utf-8 -*-
"""Dump source paragraphs (skip 5-line header, count non-empty lines)."""
import sys, io

t = io.open(sys.argv[1], encoding='utf-8').read()
ls = t.split('\n')[5:]
ps = [l for l in ls if l.strip()]
for a in sys.argv[2:]:
    i = int(a) - 1
    print('=== src seg %d ===' % (i + 1))
    print(ps[i])
    print('')
