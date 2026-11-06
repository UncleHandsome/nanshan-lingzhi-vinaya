# -*- coding: utf-8 -*-
"""人工複核：逐筆印出 記 開頭 與 所配 鈔段 開頭。"""
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']
m = {x['z']: x['c'] for x in json.load(io.open(os.path.join(D, 'out_008.json'), encoding='utf-8'))['map']}
prev = None
for z in range(300, 450):
    c = m[z]
    mark = '  <<< NEW c' if c != prev else ''
    if c != prev:
        print('\n%s\n  [鈔 c=%d] %s' % ('-' * 90, c, C[c][:70]))
    print('  z=%d | %s%s' % (z, J[z][:48], mark))
    prev = c
