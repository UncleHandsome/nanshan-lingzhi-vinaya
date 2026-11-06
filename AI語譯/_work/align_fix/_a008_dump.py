# -*- coding: utf-8 -*-
"""輸出 鈔 c 範圍 與 記 z 範圍 的全文，供人工對齊。"""
import io, os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_a008_data.json'), encoding='utf-8'))
J, C = d['ji'], d['cao']
lines = []
for c in range(17, 76):
    lines.append('\n【鈔 c=%d】len=%d\n%s' % (c, len(C[c]), C[c]))
io.open(os.path.join(D, '_a008_cao_17_75.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
lines = []
for z in range(286, 470):
    lines.append('\n【記 z=%d】len=%d\n%s' % (z, len(J[z]), J[z]))
io.open(os.path.join(D, '_a008_ji_286_469.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('ok', sum(len(C[c]) for c in range(17, 76)), sum(len(J[z]) for z in range(286, 470)))
