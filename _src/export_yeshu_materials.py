# -*- coding: utf-8 -*-
"""業疏材料：每卷一份 CSV ＋ Excel（原文、白話、譯文對應序號）"""
import io, os, re, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, '業疏材料')
os.makedirs(OUT, exist_ok=True)


def vol_of(key):
    j = key.split('_', 1)[1] if '_' in key else ''
    if j.startswith('卷首'):
        return '卷首'
    m = re.match(r'卷[上中下]', j)
    if m:
        return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j


def load_offsets():
    import json
    p = os.path.join(B, 'AI語譯', '_work', 'ys_offsets_final.json')
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return {}


def _off_for(off, i):
    if isinstance(off, (int, float)):
        return int(off)
    for a, b, o in off:
        if a <= i <= b:
            return int(o)
    return 0


def main():
    OFF = load_offsets()
    rows_by_vol = {}
    chunks = []
    tt_all, pref = [], {}
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
        pref[k] = len(tt_all)
        tt_all += tt
        chunks.append((k, sp, tt))
    for k, sp, tt in chunks:
        v = vol_of(k)
        rows_by_vol.setdefault(v, [])
        off = OFF.get(k, 0)
        for i, o in enumerate(sp, 1):
            g = pref[k] + (i - 1) + _off_for(off, i - 1)
            t = tt_all[g] if 0 <= g < len(tt_all) else ''
            rows_by_vol[v].append([k, v, i, o, t, g + 1])

    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
    except Exception:
        wb = None

    for v, rows in rows_by_vol.items():
        fn = os.path.join(OUT, '%s.csv' % v)
        with io.open(fn, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['分塊', '卷', '序號', '原文', '白話', '譯文序號(可改)'])
            w.writerows(rows)
        if wb is not None:
            ws = wb.create_sheet(v[:31])
            ws.append(['分塊', '卷', '序號', '原文', '白話', '譯文序號(可改)'])
            for c in ws[1]:
                c.font = Font(bold=True)
                c.fill = PatternFill('solid', fgColor='EFE7D6')
            for r in rows:
                ws.append(r)
            for col, wd in zip('ABCDEF', (16, 6, 6, 80, 55, 14)):
                ws.column_dimensions[col].width = wd
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical='top')
    if wb is not None:
        wb.save(os.path.join(OUT, '業疏材料.xlsx'))
    io.open(os.path.join(OUT, '使用說明.txt'), 'w', encoding='utf-8').write(
        '業疏對照材料\n===========\n'
        '1. 每卷一份 CSV（卷首、卷一…卷四），另有 業疏材料.xlsx（每卷一個工作表）。\n'
        '2. 欄位：分塊（原始檔）、卷、序號（該卷內第幾段原文）、原文、白話、譯文序號(可改)。\n'
        '3. 目前「白話」是用「譯文序號」去取譯文（預設 i+2，因為譯文開頭多 2 段）。\n'
        '4. 若某段白話對不上，把該列的「譯文序號」改成正確的譯文段號即可；留空表示不顯示白話。\n'
        '5. 譯文總表在 AI語譯/out/03_業疏/*.txt（每塊一個檔，段落以空行分隔）。\n')
    print('卷', list(rows_by_vol), 'rows', sum(len(v) for v in rows_by_vol.values()))


if __name__ == '__main__':
    main()
