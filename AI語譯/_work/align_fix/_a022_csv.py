# -*- coding: utf-8 -*-
import io, csv, json, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\篇20_對施興治.csv'
rows = list(csv.reader(io.open(p, encoding='utf-8-sig')))
print('header', rows[0])
ji = [r for r in rows[1:] if r[0] == '記']
cao = [r for r in rows[1:] if r[0] == '鈔']
print('cao', len(cao), 'ji', len(ji))
for r in cao:
    print('CAO', r[1], r[2][:28])
for r in ji:
    print('JI', r[1], 'map=', repr(r[4]), r[2][:34])
