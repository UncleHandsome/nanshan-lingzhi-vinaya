# -*- coding: utf-8 -*-
"""修正 05_拾毗尼義鈔 01b/02b：把多段落的譯文壓成單一段落（每段只能一段文字）。"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROUT = os.path.join(B, 'AI語譯', '_work', 'misstr')


def flat(s):
    s = re.sub(r'\s*\n\s*', '', s.strip())
    return s


for n, key in ((6, '01b_卷上之一'), (7, '02b_卷上之二')):
    arr = json.load(io.open(os.path.join(ROUT, 'out_%02d.json' % n), encoding='utf-8'))
    tp = os.path.join(B, 'AI語譯', 'out', '05_拾毗尼義鈔', key + '.txt')
    ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    print(key, '目前段數', len(ps))
    # 重新由批次檔取原文段，改用 out_nn 的譯文（壓平）
    segs = {int(x['seg']): flat(x['text']) for x in arr}
    # 目前檔案已壞：重建為 4 段（以批次檔 seg1..4 為序）
    new = [segs[i] for i in sorted(segs)]
    io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
    print(key, '重寫段數', len(new))
