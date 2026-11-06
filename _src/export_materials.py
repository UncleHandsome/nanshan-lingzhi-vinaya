# -*- coding: utf-8 -*-
"""匯出合編材料：每篇一份 CSV ＋ 一本 Excel（鈔段／記段／AI 對應）"""
import io, os, re, json, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '合編材料')
os.makedirs(OUT, exist_ok=True)
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(src, tr):
    S = os.path.join(B, 'TXT_分卷', src)
    T = os.path.join(B, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((k, sp, tt))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')


def sections():
    secs, cur = [], None
    for k, sp, tt in load('01_行事鈔', '01_行事鈔'):
        for i, o in enumerate(sp):
            if PATS2.match(o.strip()):
                continue
            m = PATS.match(o)
            if m:
                if any(x['no'] == m.group(2) for x in secs):
                    cur = next(x for x in secs if x['no'] == m.group(2))
                else:
                    cur = dict(name=m.group(1), no=m.group(2), items=[])
                    secs.append(cur)
                continue
            if cur is not None:
                cur['items'].append((o, tt[i] if i < len(tt) else ''))
    return secs


Z2S = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13, 13, 13,
       14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


def zsecs():
    zj = []
    for k, sp, tt in load('資持記_細分', '資持記'):
        zj += list(zip(sp, tt))
    ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
    valid = [x['name'] for x in sections()]
    z = dict(name='序', items=[])
    zs = [z]
    for o, t in zj:
        m = ZP.search(o) or ZP.search(t)
        if m and any(v.startswith(m.group(1)) or m.group(1) in v for v in valid):
            z = dict(name=m.group(1), items=[])
            zs.append(z)
        z['items'].append((o, t))
    return zs


def zitems_for(idx, zs):
    out = []
    for i, sec in enumerate(zs):
        if i < len(Z2S) and Z2S[i] == idx:
            out += sec['items']
    return out


def build_zi(secs, zs):
    ZI = {i: [] for i in range(len(secs))}
    for i, sec in enumerate(zs):
        if i < len(Z2S):
            ZI[Z2S[i]] += sec['items']
    if len(ZI[13]) > 122:
        ZI[12] = ZI[12] + ZI[13][:122]
        ZI[13] = ZI[13][122:]
    if len(ZI[11]) > 90:
        ZI[12] = [ZI[11][-1]] + ZI[12]
        ZI[11] = ZI[11][:-1]
    ZI[29] = ZI[29][:28]
    return ZI


def main():
    secs = sections()
    zs = zsecs()
    ZI = build_zi(secs, zs)
    try:
        AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
    except Exception:
        AM = {}
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
    except Exception:
        wb = None
    total = 0
    for idx, sec in enumerate(secs):
        C = sec['items']
        Z = ZI.get(idx, [])
        if not C:
            continue
        am = AM.get(str(idx)) or []
        rows = []
        rows.append(['類型', '序號', '原文', '白話', '對應鈔號(可改)'])
        for i, (o, t) in enumerate(C, 1):
            rows.append(['鈔', i, o, t, ''])
        for i, (o, t) in enumerate(Z, 1):
            c = ''
            if i - 1 < len(am):
                c = int(am[i - 1]) + 1
            rows.append(['記', i, o, t, c])
        fn = os.path.join(OUT, '篇%02d_%s.csv' % (idx + 1, sec['name']))
        with io.open(fn, 'w', encoding='utf-8-sig', newline='') as fh:
            csv.writer(fh).writerows(rows)
        total += len(rows) - 1
        if wb is not None:
            ws = wb.create_sheet('第%02d篇 %s' % (idx + 1, sec['name'])[:31])
            for r in rows:
                ws.append(r)
            ws.column_dimensions['A'].width = 6
            ws.column_dimensions['B'].width = 6
            ws.column_dimensions['C'].width = 90
            ws.column_dimensions['D'].width = 60
            ws.column_dimensions['E'].width = 14
    if wb is not None:
        wb.save(os.path.join(OUT, '合編材料.xlsx'))
    print('篇', len(secs), '列', total)

    readme = os.path.join(OUT, '使用說明.txt')
    io.open(readme, 'w', encoding='utf-8').write(
        '句級合編材料（供人工核對）\n'
        '================================\n'
        '1. 每一篇一份 CSV（篇NN_篇名.csv），也可以用 合編材料.xlsx（每篇一個工作表）。\n'
        '2. 欄位：類型（鈔／記）、序號（該篇內編號）、原文、白話、對應鈔號。\n'
        '3. 「對應鈔號」只對【記】列有意義：填「這一段記文是在解釋第幾號鈔段」。\n'
        '   目前填的是 AI 判定的結果，可直接修改；留空＝沿用上一個記段的號碼。\n'
        '4. 若要重新生成合編：改好 CSV 後執行\n'
        '     python _src/build_from_csv.py\n'
        '   會依「對應鈔號」把記文插到對應鈔段之後，重新產生 docx（PDF 再用 LibreOffice 轉）。\n'
        '5. 鈔段與記段都是原始分段，不可刪列、不可改序號；只改「對應鈔號」欄。\n')
    print('readme ok')


if __name__ == '__main__':
    main()
