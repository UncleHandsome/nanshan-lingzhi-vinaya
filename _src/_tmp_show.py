# -*- coding: utf-8 -*-
import sys, io, re

def paras(path):
    t = io.open(path, encoding='utf-8').read()
    return [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]

def srcparas(path):
    lines = io.open(path, encoding='utf-8').read().split('\n')
    lines = lines[5:]
    return [l.strip() for l in lines if l.strip()]

if __name__ == '__main__':
    mode = sys.argv[1]
    path = sys.argv[2]
    seg = int(sys.argv[3])
    ps = paras(path) if mode == 'out' else srcparas(path)
    print('TOTAL=%d' % len(ps))
    print(ps[seg-1])
