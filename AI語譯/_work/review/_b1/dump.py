# -*- coding: utf-8 -*-
"""輸出逐條對照稿（原文／現行譯文／意見／建議）。"""
import os, io, json, re, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WORK = os.path.join(B, 'AI語譯', '_work', 'review', '_b1')
items = json.load(io.open(os.path.join(WORK, 'items.json'), encoding='utf-8'))

lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else len(items)

buf = []
for i, it in enumerate(items[lo:hi], start=lo + 1):
    buf.append('#' * 70)
    buf.append('[%02d] %s | %s/%s#%d | %s | %s' % (
        i, it['gid'], it['book2'], it['chunk2'], it['seg2'], it['level'], it['type']))
    buf.append('--- 原文起首(意見稱)：' + it.get('quote', ''))
    buf.append('--- 原文：' + it['mat'][1])
    buf.append('--- 現行譯文：' + it['cur'])
    buf.append('--- 問題：' + it.get('problem', ''))
    buf.append('--- 依據：' + it.get('basis', ''))
    buf.append('--- 建議：' + it.get('suggest', ''))
    buf.append('')
print('\n'.join(buf))
