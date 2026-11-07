# -*- coding: utf-8 -*-
"""（舊版，僅供追溯）一次重建全部成品的早期腳本。

**現在請照 交接/交接_2026-11-07.md 第二節的順序重建**，本檔引用的
build_book.py / hebian_ju.py / chk_all_counts.py 已改由新流程取代，
直接執行會失敗。保留原因：說明 戒疏／資持記 對照本 的 build_book.py 參數。

用法（歷史）：
    python _src/rebuild_all.py            # 全部重建（含 PDF）
    python _src/rebuild_all.py --no-pdf   # 只重建 docx 與網站
"""
import os, io, re, subprocess, sys, glob, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'

BOOKS = [
    # tag,         title,                  prefix,    srcdir
    ('01_行事鈔', '四分律刪繁補闕行事鈔', '行事鈔', '01_行事鈔'),
    ('02_戒疏', '四分律含注戒本疏', '戒疏', '02_戒疏'),
    # 04 尼鈔、05 尼義鈔 的文言改由 build_ju_vol.py 以句讀本產生
    ('資持記', '四分律行事鈔資持記', '資持記', '資持記_細分'),
]
YESHU = ('03_業疏', '四分律刪補隨機羯磨疏', '業疏', '03_業疏')


def run(cmd, **kw):
    print('>', ' '.join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    if r.stdout.strip():
        print(r.stdout.strip()[-3000:])
    if r.returncode != 0:
        print(r.stderr.strip()[-3000:])
    return r.returncode


def counts_ok():
    r = subprocess.run([PY, os.path.join(B, '_src', 'chk_all_counts.py')], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    out = r.stdout
    print(out)
    bad = 0
    for line in out.split('\n'):
        m = re.search(r'mismatch\s+(\d+)', line)
        if m and int(m.group(1)) > 0:
            bad += int(m.group(1))
    return bad == 0


def main():
    args = sys.argv[1:]
    no_pdf = '--no-pdf' in args
    with_yeshu = '--with-yeshu' in args
    if not counts_ok():
        print('!! 段數不合，停止重建')
        return 1

    books = list(BOOKS) + ([YESHU] if with_yeshu else [])
    for tag, title, prefix, srcdir in books:
        run([PY, os.path.join(B, '_src', 'build_book.py'), tag, title, prefix, srcdir])

    # 行事鈔另用 build_vol.py（上／中／下卷）
    run([PY, os.path.join(B, '_src', 'build_vol.py')])
    # 尼鈔、尼義鈔以句讀原文分卷出書
    run([PY, os.path.join(B, '_src', 'build_ju_vol.py'), '--no-pdf'])

    # 合編（句讀對照本已改由 build_ju_vol.py 出分卷本）
    run([PY, os.path.join(B, '_src', 'hebian_ju.py')])

    if not no_pdf:
        docxs = sorted(glob.glob(os.path.join(B, '白話', '*.docx')))
        docxs = [d for d in docxs if not os.path.basename(d).startswith('~$')]
        pdfdir = os.path.join(B, '白話', 'PDF')
        os.makedirs(pdfdir, exist_ok=True)
        for d in docxs:
            print('convert', os.path.basename(d))
            subprocess.run([SOFFICE, '--headless', '--norestore',
                            '-env:UserInstallation=file:///C:/Temp/lo_profile_rebuild',
                            '--convert-to', 'pdf', '--outdir', pdfdir, d],
                           capture_output=True)
        # 注意：PDF 一律放 白話/PDF/，不要再搬到子資料夾（2026-11-07 曾因搬到
        # 白話/對照本/ 而被清理程序整批移出專案，導致 49 個 PDF 消失）。

    # 網站
    run([PY, os.path.join(B, '_src', 'site2.py')])
    run([PY, os.path.join(B, '_src', 'build_appendix.py')])
    print('done')
    return 0


if __name__ == '__main__':
    sys.exit(main())
