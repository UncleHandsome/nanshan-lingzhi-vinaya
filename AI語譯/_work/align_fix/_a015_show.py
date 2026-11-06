# -*- coding: utf-8 -*-
"""Print side-by-side review table: 記段 head vs assigned 鈔段 head."""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')


def load(p):
    txt = io.open(p, encoding='utf-8').read()
    out = {}
    for part in txt.split('\n\n'):
        part = part.strip()
        if not part:
            continue
        m = re.match(r'\[(z|c)(\d+)\] len=(\d+)\n(.*)$', part, re.S)
        if m:
            out[int(m.group(2))] = m.group(4)
    return out


Z = load(os.path.join(AD, '_a015_Z.txt'))
C = load(os.path.join(AD, '_a015_C.txt'))
MAP = [m['c'] for m in json.load(io.open(os.path.join(AD, 'out_015.json'), encoding='utf-8'))['map']]
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for zi in range(lo, hi):
    ci = MAP[zi]
    print('z%-3d|c%-3d  %s' % (zi, ci, Z[zi][:46].replace('\n', ' ')))
    print('      ^     %s' % C[ci][:46].replace('\n', ' '))
