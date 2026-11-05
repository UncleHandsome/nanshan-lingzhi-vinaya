# -*- coding: utf-8 -*-
"""Print paragraph count of translation txt files.

Usage: python _src/paracount.py <file> [<file> ...]

A paragraph is a non-empty chunk separated by one or more blank lines.
"""
import sys, io, re, os

def paras(path):
    t = io.open(path, encoding='utf-8').read()
    return [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]

if __name__ == '__main__':
    for p in sys.argv[1:]:
        ps = paras(p)
        print('%s\tparas=%d\tchars=%d' % (os.path.basename(p), len(ps), len(io.open(p, encoding='utf-8').read())))
