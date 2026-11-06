# -*- coding: utf-8 -*-
"""依使用者提供的卷一診斷，寫入帶符號的分塊位移；支援分段覆寫"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
P = os.path.join(B, 'AI語譯', '_work', 'ys_offsets_final.json')
cur = json.load(io.open(P, encoding='utf-8')) if os.path.exists(P) else {}

# 使用者診斷（卷一首段的分段覆寫：[起,迄,位移]）
FIX = {
    '01a_卷一之一': [[0, 34, 0], [35, 999, 1]],
    '01b_卷一之一': 4,
    '02a_卷一之二': 7,
    '02b_卷一之二': -4,
    '03a_卷一之三': -2,
    '03b_卷一之三': -3,
    '04a_卷一之四': 5,
    '05a_卷一之五': 15,
    '05b_卷一之五': -13,
    '06a_卷一之六': -18,
    '06b_卷一之六': -21,
}
cur.update(FIX)
json.dump(cur, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('寫入', len(FIX), '塊；目前共', len(cur))
for k in sorted(FIX):
    print('  %-14s %s' % (k, FIX[k]))
