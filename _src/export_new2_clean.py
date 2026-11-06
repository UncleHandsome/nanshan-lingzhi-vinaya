# -*- coding: utf-8 -*-
"""new2_clean.csv → new2_clean.xlsx（每篇一表）"""
import io, os, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '合編材料')
rows = list(csv.DictReader(io.open(os.path.join(MAT, 'new2_clean.csv'), encoding='utf-8-sig')))

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

wb = openpyxl.Workbook()
wb.remove(wb.active)
by = {}
for r in rows:
    by.setdefault(r['pian'], []).append(r)
for pian, rs in by.items():
    ws = wb.create_sheet(pian[:31])
    head = ['鈔序', '記對應（原文）', '參照工作表', '記號起', '記號迄', '說明摘要']
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill('solid', fgColor='EFE7D6')
    for r in rs:
        ws.append([r['chao'], r['refs'], r['sheets'], r['nmin'], r['nmax'], r['note']])
    for col, wd in zip('ABCDEF', (10, 34, 14, 8, 8, 70)):
        ws.column_dimensions[col].width = wd
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')
wb.save(os.path.join(MAT, 'new2_clean.xlsx'))
print('saved new2_clean.xlsx sheets', len(by), 'rows', len(rows))
