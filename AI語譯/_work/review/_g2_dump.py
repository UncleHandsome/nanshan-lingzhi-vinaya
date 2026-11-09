# -*- coding: utf-8 -*-
import json, io, sys

data = json.loads(io.open(r'AI語譯\_work\review\_g2_rows.json', encoding='utf-8').read())
lo = int(sys.argv[1]); hi = int(sys.argv[2])
blocks = []
for i, r in enumerate(data):
    if not (lo <= i + 1 <= hi):
        continue
    blocks.append('##### [%d] %s | %s | %s | %s | %s' % (i + 1, r['gid'], r['book'], r['chunk'], r['seg'], r['level']))
    blocks.append('PROBLEM: ' + r['problem'])
    blocks.append('SUGGEST: ' + r['suggestion'])
    blocks.append('ORIG: ' + r['orig'])
    blocks.append('CURRENT: ' + r['current'])
    blocks.append('')
io.open(r'AI語譯\_work\review\_g2_dump_%d_%d.txt' % (lo, hi), 'w', encoding='utf-8').write('\n'.join(blocks))
print('ok', len(blocks))
