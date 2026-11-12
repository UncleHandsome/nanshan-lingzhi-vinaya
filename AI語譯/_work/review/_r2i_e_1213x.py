# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2i_lib as L
HERE = os.path.dirname(os.path.abspath(__file__))
D = '10d_中三下'
A = '11a_中四上'
edits = [
 dict(chunk=D, seg=46, old='通達外其他各部者', new='兼通其他部派的律典', why='1213-0009 通外部'),
 dict(chunk=A, seg=1, old='科註部分分為兩段', new='（鈔文的）注文分為兩段', why='1213-0012 注=鈔注'),
 dict(chunk=A, seg=1, old='普遍涵蓋了整個法界的一切行法', new='普遍涵蓋整個法界的一切境事', why='1213-0012 刪增譯「行法」'),
]
apply = '--apply' in sys.argv
bad = 0
for ch in (D, A):
    o = L.load_out(ch)
    for e in [x for x in edits if x['chunk'] == ch]:
        c = o['segs'][e['seg'] - 1].count(e['old'])
        if c != 1:
            bad += 1
            print('BAD', c, ch, e['seg'], e['old'][:50])
print('bad', bad)
if bad:
    raise SystemExit('abort')
if apply:
    for ch in (D, A):
        es = [x for x in edits if x['chunk'] == ch]
        if es:
            L.apply_edits(ch, es, note='r2 1181-1330')
    json.dump(edits, open(os.path.join(HERE, '_r2i_edits_1213_extra.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied')
