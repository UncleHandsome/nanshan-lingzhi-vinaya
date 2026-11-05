# -*- coding: utf-8 -*-
"""Dump given segments of out/src side by side to a UTF-8 text file."""
import sys, io, re

def outparas(path):
    t = io.open(path, encoding='utf-8').read()
    return [x for x in re.split(r'\r?\n\r?\n', t) if x.strip()]

def srcparas(path):
    lines = io.open(path, encoding='utf-8').read().split('\n')
    return [l.strip() for l in lines[5:] if l.strip()]

if __name__ == '__main__':
    book = sys.argv[1]
    chunk = sys.argv[2]
    segs = [int(x) for x in sys.argv[3].split(',')]
    outp = 'AI語譯/out/%s/%s.txt' % (book, chunk)
    srcp = 'TXT_分卷/%s/%s.txt' % (book, chunk)
    o = outparas(outp)
    s = srcparas(srcp)
    w = io.open('_src/_tmp_view.txt', 'w', encoding='utf-8')
    w.write('OUT total=%d SRC total=%d\n' % (len(o), len(s)))
    for seg in segs:
        w.write('\n===== SEG %d =====\n' % seg)
        w.write('--- SRC ---\n%s\n' % (s[seg-1].strip() if seg-1 < len(s) else '<none>'))
        w.write('--- OUT ---\n%s\n' % (o[seg-1] if seg-1 < len(o) else '<none>'))
    w.close()
    print('ok')
