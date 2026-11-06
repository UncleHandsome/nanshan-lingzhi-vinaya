# -*- coding: utf-8 -*-
"""比對「AI 對應」與「修正對應」，輸出差異報告"""
import io, os, csv, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '合編材料')
OUT = os.path.join(MAT, '修正差異.txt')


def main():
    import openpyxl
    p = os.path.join(MAT, '合編_並排對照.xlsx')
    if not os.path.exists(p):
        print('no xlsx')
        return
    wb = openpyxl.load_workbook(p, data_only=True)
    lines = []
    total = changed = 0
    for ws in wb.worksheets:
        name = ws.title
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[3]:
                continue
            z = row[3]
            ai = row[6]
            fix = row[7] if len(row) > 7 else None
            total += 1
            if fix not in (None, '') and str(fix) != str(ai):
                changed += 1
                lines.append('%s　記%-4s AI=%-5s 修正=%-5s ｜ %s' % (
                    name, z, ai, fix, (row[4] or '')[:38]))
    io.open(OUT, 'w', encoding='utf-8').write(
        '修正差異報告\nAI 對應 vs 人工修正\n共 %d 段記文，其中 %d 段被修改\n\n' % (total, changed)
        + '\n'.join(lines) + '\n')
    print('記段', total, '修改', changed, '→', OUT)


if __name__ == '__main__':
    main()
