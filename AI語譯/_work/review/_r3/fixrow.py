# -*- coding: utf-8 -*-
"""fixrow.py NNN items fixed rej doubt note -- replace the last row whose first field is NNN."""
import sys, io
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DONE = ROOT + r'\AI語譯\_work\review\r3_done.tsv'
n = sys.argv[1]
vals = sys.argv[2:]
raw = open(DONE, 'rb').read().decode('utf-8-sig')
lines = raw.split('\n')
for i in range(len(lines) - 1, -1, -1):
    if lines[i].split('\t')[0] == n:
        lines[i] = '\t'.join([n] + vals)
        print('row', i + 1, 'replaced')
        break
else:
    print('NOT FOUND', n)
open(DONE, 'wb').write(('\ufeff' + '\n'.join(lines)).encode('utf-8'))
