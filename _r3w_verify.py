import sys, os
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

expected = {
 ('01_行事鈔','08a_卷中之四'): [63,64,65],
 ('01_行事鈔','08b_卷中之四'): [37],
 ('01_行事鈔','08c_卷中之四'): [2,3,6,7],
 ('01_行事鈔','10a_卷下之二'): [6],
 ('01_行事鈔','12a_卷下之四'): [16,19,22,24],
 ('02_戒疏','03b_卷一下之一'): [104,105,111,115,117],
 ('02_戒疏','04a_卷一下之二'): [144,147,148,150,156,157],
 ('02_戒疏','05a_卷二上之一'): [108,112,114,118,123],
 ('02_戒疏','05b_卷二上之一'): [51,52,62],
 ('02_戒疏','05d_卷二上之一'): [138],
 ('02_戒疏','06a_卷二上之二'): [3,21,22,27,28,29,31,35,36,38,43,67,68,72,74,75,97,98,101,102,103,104,106,131],
 ('02_戒疏','06b_卷二上之二'): [2,3,5,6,7,8,10,11,12,14,19,20,29,32,33,35,38,39],
 ('02_戒疏','09a_卷二下之二'): [120,121,124,125,126,127,133],
}
ok = True
for (book, chunk), idxs in expected.items():
    cur = read_text(book, chunk)
    bak = open(os.path.join(BASE,'歸檔','rere修正前',book,chunk+'_y.txt'),'rb').read().decode('utf-8')
    cp, bp = split_parts(cur), split_parts(bak)
    cb, bb = cp[0::2], bp[0::2]
    if len(cb) != len(bb):
        print('BLOCK COUNT MISMATCH', book, chunk, len(cb), len(bb)); ok=False; continue
    diffs = [i+1 for i in range(len(cb)) if cb[i] != bb[i]]
    sep_same = cp[1::2] == bp[1::2]
    print(f'{book}/{chunk}: blocks={len(cb)} diffs={diffs} sep_same={sep_same}')
    if diffs != idxs:
        print('  !! expected', idxs); ok=False
    if not sep_same:
        ok=False
print('ALL OK' if ok else 'PROBLEMS')
