# -*- coding: utf-8 -*-
"""印出某檔某段的指定字元區間（供長段落檢視）。用法: python _r2c_cut.py 1499 1 1800 1800"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

n = int(sys.argv[1]); seq = int(sys.argv[2])
start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
ln = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
r = [x for x in L.parse_review(n) if x['seq'] == seq][0]
o = L.Out(r['book'], r['chunk'])
t = o.segs[r['seg'] - 1]
print('LEN=%d START=%d' % (len(t), start))
s = t[start:start + ln]
for i in range(0, len(s), 100):
    print(s[i:i + 100])
