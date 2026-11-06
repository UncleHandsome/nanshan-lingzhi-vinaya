# -*- coding: utf-8 -*-
import sys, docx, re
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\合編_人工對齊版.docx'
d = docx.Document(p)
paras = [x.text.strip() for x in d.paragraphs]
start = 8676
end = None
for i in range(start+1, len(paras)):
    if paras[i].startswith('篇19') or '鉢器制聽篇' in paras[i]:
        end = i; break
print('end marker', end)
n_c = n_j = 0
for i in range(start, end):
    t = paras[i]
    if t.startswith('【鈔】'):
        n_c += 1
        print('C%02d' % n_c, i, '|', t[3:40])
    elif t.startswith('【記】'):
        n_j += 1
        print('  Z%03d' % n_j, i, '|', t[3:40])
print('total C', n_c, 'Z', n_j)
