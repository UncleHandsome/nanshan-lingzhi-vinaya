# -*- coding: utf-8 -*-
"""Spot-check out_018.json: show each c-boundary with 記 and 鈔 heads."""
import io, os, json, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
J = json.load(io.open(os.path.join(AD, '018.json'), encoding='utf-8'))
O = json.load(io.open(os.path.join(AD, 'out_018.json'), encoding='utf-8'))
zj = {it['z']: it['text'] for it in J['items']}
cc = {c['c']: c['text'] for c in J['cand']}
mp = O['map']
prev = None
for m in mp:
    if m['c'] != prev:
        print('--- z%d -> c%d' % (m['z'], m['c']))
        print(' 記:', zj[m['z']][:60])
        print(' 鈔:', cc.get(m['c'], '?')[:60])
        prev = m['c']
print()
print('total', len(mp), 'zfirst', mp[0]['z'], 'zlast', mp[-1]['z'],
      'mono', all(mp[i]['c'] <= mp[i+1]['c'] for i in range(len(mp)-1)),
      'inrange', all(0 <= m['c'] <= 95 for m in mp))
