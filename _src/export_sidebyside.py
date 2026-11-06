# -*- coding: utf-8 -*-
"""產生「並排對照」Excel：左鈔右記，附 AI 對應與可填的修正欄"""
import io, os, re, csv, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '合編材料')


def read_csv(p):
    with io.open(p, encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def main():
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    head = ['鈔序', '鈔文', '鈔白話', '記序', '記文', '記白話', 'AI對應', '修正對應']
    for f in sorted(glob.glob(os.path.join(MAT, '篇*.csv'))):
        name = os.path.basename(f)[:-4]
        rows = read_csv(f)
        chao = [r for r in rows if r['類型'] == '鈔']
        ji = [r for r in rows if r['類型'] == '記']
        by_c = {}
        last = 1
        for r in ji:
            v = (r.get('對應鈔號(可改)') or '').strip()
            try:
                c = int(v) if v else last
            except ValueError:
                c = last
            c = max(1, min(len(chao), c))
            last = c
            by_c.setdefault(c, []).append(r)
        ws = wb.create_sheet(name[:31])
        ws.append(head)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill('solid', fgColor='EFE7D6')
        for i, cr in enumerate(chao, 1):
            group = by_c.get(i, [])
            first = True
            if not group:
                ws.append([i, cr['原文'], cr['白話'], '', '', '', '', ''])
            for jr in group:
                if first:
                    ws.append([i, cr['原文'], cr['白話'], jr['序號'], jr['原文'], jr['白話'],
                               jr.get('對應鈔號(可改)', ''), ''])
                    first = False
                else:
                    ws.append(['', '', '', jr['序號'], jr['原文'], jr['白話'],
                               jr.get('對應鈔號(可改)', ''), ''])
        ws.column_dimensions['A'].width = 6
        ws.column_dimensions['B'].width = 60
        ws.column_dimensions['C'].width = 42
        ws.column_dimensions['D'].width = 6
        ws.column_dimensions['E'].width = 70
        ws.column_dimensions['F'].width = 42
        ws.column_dimensions['G'].width = 9
        ws.column_dimensions['H'].width = 9
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
    out = os.path.join(MAT, '合編_並排對照.xlsx')
    wb.save(out)
    print('saved', out, 'sheets', len(wb.sheetnames))


if __name__ == '__main__':
    main()
