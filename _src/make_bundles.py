# -*- coding: utf-8 -*-
"""把六書＋合編的 Word／PDF 打包成 ZIP，供下載頁「打包下載」。

輸出到 `打包下載_ZIP/`：
  白話對照本_全部.zip        所有 128 檔
  白話對照本_單欄.zip        單欄 DOCX＋PDF
  白話對照本_雙欄.zip        雙欄 DOCX＋PDF
  白話對照本_<書>.zip        各書（單＋雙欄）
"""
import glob
import os
import zipfile

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '打包下載_ZIP')
DIRS = [
    ('白話對照本_標楷_單欄_DOCX', '單欄'),
    ('白話對照本_標楷_單欄_PDF', '單欄'),
    ('白話對照本_標楷_雙欄_DOCX', '雙欄'),
    ('白話對照本_標楷_雙欄_PDF', '雙欄'),
]
BOOKS = [
    ('行事鈔', '四分律刪繁補闕行事鈔'),
    ('戒疏', '四分律含注戒本疏行宗記'),
    ('業疏', '四分律刪補隨機羯磨疏'),
    ('尼鈔', '四分比丘尼鈔'),
    ('義鈔', '四分律拾毗尼義鈔'),
    ('資持記', '四分律行事鈔資持記'),
    ('合編本', '四分律行事鈔資持記・句級合編'),
]


def book_of(fn):
    if '合編' in fn:
        return '合編本'
    for short, full in BOOKS[:-1]:
        if full in fn:
            return short
    for k in ('行事鈔', '戒疏', '業疏', '尼鈔', '義鈔', '資持記'):
        if k in fn:
            return k
    return '其他'


def collect():
    items = []
    for d, layout in DIRS:
        for p in sorted(glob.glob(os.path.join(B, d, '*'))):
            if os.path.isfile(p) and p.lower().endswith(('.docx', '.pdf')):
                items.append((p, layout))
    return items


def write_zip(name, items):
    os.makedirs(OUT, exist_ok=True)
    fp = os.path.join(OUT, name)
    with zipfile.ZipFile(fp, 'w', compression=zipfile.ZIP_STORED) as zf:
        for p, _layout in items:
            zf.write(p, arcname=os.path.basename(p))
    print('%-28s %3d 檔  %6.1f MB' % (name, len(items), os.path.getsize(fp) / 1048576))
    return fp


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.zip')):
        os.remove(f)
    items = collect()
    print('來源檔案', len(items))
    write_zip('白話對照本_全部.zip', items)
    for short, _full in BOOKS:
        sub = [(p, l) for p, l in items if book_of(os.path.basename(p)) == short]
        if sub:
            write_zip('白話對照本_%s.zip' % short, sub)
    tot = sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT, '*.zip')))
    print('全部 ZIP %d 個，合計 %.1f MB' % (len(glob.glob(os.path.join(OUT, '*.zip'))), tot / 1048576))


if __name__ == '__main__':
    main()
