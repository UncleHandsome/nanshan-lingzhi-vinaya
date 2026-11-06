# -*- coding: utf-8 -*-
"""由 splits 推導 bounds（篇18-30 用）"""
import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SP = os.path.join(B, 'AI語譯', '_work', 'pian_split_out')
BD = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')

for p in range(18, 31):
    fp = os.path.join(SP, 'split_篇%02d.json' % p)
    if not os.path.exists(fp):
        continue
    sp = json.load(io.open(fp, encoding='utf-8-sig')).get('splits', [])
    am = AM.get(str(p - 1), [])
    # 由 am 建初始界
    starts = {}
    for k, c in enumerate(am):
        c = int(c)
        if c >= 2 and c not in starts:
            starts[c] = k + 1
    # splits 覆寫：每個 target 的第一段起點
    for e in sp:
        n = int(e['n'])
        tg = [int(x) for x in e['targets']]
        for i, c in enumerate(tg):
            if i == 0:
                if c not in starts or n < starts[c]:
                    starts[c] = n
            else:
                if c not in starts:
                    starts[c] = n
    cs = sorted(starts)
    # 強制遞增
    last = 1
    bs = []
    for c in cs:
        n = max(starts[c], last)
        last = n
        bs.append({'c': c, 'n': n})
    json.dump({'bounds': bs}, io.open(os.path.join(BD, 'bounds_篇%02d.json' % p), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('篇%d 推導 %d 界' % (p, len(bs)))
