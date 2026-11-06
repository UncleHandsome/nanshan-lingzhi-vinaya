# -*- coding: utf-8 -*-
"""計算各交界記段在切分點前後的字數（漢字），輔助判斷。"""
import io, os, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix'
d = json.load(io.open(os.path.join(D, '_w009_data.json'), encoding='utf-8'))
J = d['ji']
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
cases = [
    (505, '第二。'), (518, '第三。'), (522, '第四。'), (525, '第五。'), (532, '第六。'),
    (546, '釋第一中'), (559, '第七。'), (561, '第八。'), (566, '第九。'), (568, '第十。'),
    (573, '十一。'), (574, '十二。'), (581, '十三。'), (587, '二露處不定'),
    (588, '三十捨墮'), (588, '初戒。'), (593, '餘緣中'), (593, '三中，注綿毛'),
    (536, '一磔二尺'), (490, '大妄戒'), (475, '殺戒。'), (497, '四分律行事鈔資持記中二'),
]
for z, sep in cases:
    t = J[z]
    i = t.find(sep)
    if i < 0:
        print('z%d sep %r NOT FOUND :: %s' % (z, sep, t[:60]))
        continue
    pre, post = han(t[:i]), han(t[i:])
    print('z%-4d sep=%-14s pre=%-3d post=%-3d  %s' % (z, sep, len(pre), len(post), t[max(0, i-25):i+30]))
