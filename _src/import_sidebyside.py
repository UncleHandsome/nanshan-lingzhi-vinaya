# -*- coding: utf-8 -*-
"""把「並排對照.xlsx」的修正對應寫回 篇NN CSV"""
import io, os, csv, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
MAT = os.path.join(B, '合編材料')


def main():
    import openpyxl
    p = os.path.join(MAT, '合編_並排對照.xlsx')
    wb = openpyxl.load_workbook(p, data_only=True)
    changed = 0
    for ws in wb.worksheets:
        name = ws.title
        cf = os.path.join(MAT, name + '.csv')
        if not os.path.exists(cf):
            print('no csv for', name)
            continue
        fix = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row:
                continue
            z = row[3]
            v = row[7] if len(row) > 7 else None
            if z and v not in (None, ''):
                try:
                    fix[int(z)] = int(v)
                except (TypeError, ValueError):
                    pass
        if not fix:
            continue
        with io.open(cf, encoding='utf-8-sig') as fh:
            rows = list(csv.DictReader(fh))
        n = 0
        for r in rows:
            if r['類型'] == '記':
                try:
                    z = int(r['序號'])
                except ValueError:
                    continue
                if z in fix and str(fix[z]) != str(r['對應鈔號(可改)']):
                    r['對應鈔號(可改)'] = str(fix[z])
                    n += 1
        if n:
            with io.open(cf, 'w', encoding='utf-8-sig', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=['類型', '序號', '原文', '白話', '對應鈔號(可改)'])
                w.writeheader()
                w.writerows(rows)
            changed += n
            print(name, '更新', n)
    print('total updated', changed)


if __name__ == '__main__':
    main()
