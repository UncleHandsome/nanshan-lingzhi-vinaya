# -*- coding: utf-8 -*-
import io, os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
def load(fn, tag):
    s = io.open(os.path.join(D, fn), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\[' + tag + r'(\d+)\] (.*?)(?=\n\n|\Z)', s, re.S):
        out[int(m.group(1))] = m.group(2).strip()
    return out
Z = load('_t020_ji.txt', 'z'); C = load('_t020_cao.txt', 'c')
O = json.load(io.open(os.path.join(D, 'out_020.json'), encoding='utf-8'))
mp = O['map']
print('n', len(mp), 'z range', mp[0]['z'], mp[-1]['z'])
prev = None
for m in mp:
    if m['c'] != prev:
        print('\n=== c%d | %s' % (m['c'], C[m['c']][:34]))
        prev = m['c']
    print('   z%-3d %s' % (m['z'], Z[m['z']][:46]))
