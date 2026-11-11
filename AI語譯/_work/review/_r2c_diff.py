# -*- coding: utf-8 -*-
"""比較材料譯文與 out 當前段，輸出字元級差異（供 RELOC 判讀）。
用法: python _r2c_diff.py 1397 1
"""
import os, sys, difflib
sys.path.insert(0, os.path.dirname(__file__))
import _r2c_lib as L

n = int(sys.argv[1]); seq = int(sys.argv[2])
recs = L.parse_review(n)
r = [x for x in recs if x['seq'] == seq][0]
o = L.out_for(r['book'], r['chunk'])
seg, ratio, moved = L.locate(r['book'], r['chunk'], r['trans'], r['seg'])
cur = o.segs[seg - 1]
print('locate seg=%d ratio=%.4f moved=%s len(mat)=%d len(cur)=%d' % (
    seg, ratio, moved, len(r['trans']), len(cur)))
sm = difflib.SequenceMatcher(None, r['trans'], cur)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    print('%-8s MAT[%d:%d]=%r  CUR[%d:%d]=%r' % (tag, i1, i2, r['trans'][i1:i2],
                                                 j1, j2, cur[j1:j2]))
