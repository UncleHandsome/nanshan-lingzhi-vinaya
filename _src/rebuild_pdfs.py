# -*- coding: utf-8 -*-
"""重建白話本 PDF（業疏因分段未對齊，不重建），並把成品歸位。

流程：build_book / build_vol / build_reflow / hebian / hebian_ju → LibreOffice 轉 PDF
→ 移到 白話/對照本、白話/純白話，最後列印頁數統計。
"""
import os, re, subprocess, sys, glob, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'
OUT = os.path.join(B, '白話')

BOOKS = [
    ('02_戒疏', '四分律含注戒本疏', '戒疏', '02_戒疏'),
    ('資持記', '四分律行事鈔資持記', '資持記', '資持記_細分'),
    # 04 尼鈔、05 尼義鈔 的文言改由 build_ju_vol.py 以句讀本產生（見下）
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('>>', os.path.basename(cmd[1]), ' '.join(cmd[2:4]), 'rc=%d' % r.returncode)
    if r.stdout.strip():
        print(r.stdout.strip()[-1200:])
    if r.returncode != 0:
        print(r.stderr.strip()[-1200:])
    return r.returncode


def convert(docx):
    name = os.path.basename(docx)
    print('convert', name)
    subprocess.run([SOFFICE, '--headless', '--norestore',
                    '-env:UserInstallation=file:///C:/Temp/lo_profile_rebuild2',
                    '--convert-to', 'pdf', '--outdir', OUT, docx], capture_output=True)


def move_pdfs():
    dst_dui = os.path.join(OUT, '對照本')
    dst_qian = os.path.join(OUT, '純白話')
    os.makedirs(dst_dui, exist_ok=True)
    os.makedirs(dst_qian, exist_ok=True)
    moved = 0
    for pat, dst in (('*_白話對照本.pdf', dst_dui), ('*_全白話本.pdf', dst_qian),
                     ('行事鈔資持記合編_*.pdf', dst_dui), ('行事鈔資持記句級合編_*.pdf', dst_dui)):
        for p in glob.glob(os.path.join(OUT, pat)):
            shutil.move(p, os.path.join(dst, os.path.basename(p)))
            moved += 1
    return moved


def pages(pdf):
    try:
        r = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True, encoding='utf-8', errors='replace')
        for line in r.stdout.split('\n'):
            if line.startswith('Pages:'):
                return int(line.split()[1])
    except Exception:
        pass
    return 0


def main():
    for tag, title, prefix, srcdir in BOOKS:
        run([PY, os.path.join(B, '_src', 'build_book.py'), tag, title, prefix, srcdir])
    run([PY, os.path.join(B, '_src', 'build_vol.py')])
    run([PY, os.path.join(B, '_src', 'build_ju_vol.py'), '--no-pdf'])
    run([PY, os.path.join(B, '_src', 'hebian_ju.py')])

    docxs = [d for d in sorted(glob.glob(os.path.join(OUT, '*.docx')))
             if not os.path.basename(d).startswith('~$')]
    for d in docxs:
        convert(d)
    print('pdfs converted', len(docxs))
    n = move_pdfs()
    print('pdfs moved', n)

    tot = 0
    rows = []
    for p in sorted(glob.glob(os.path.join(OUT, '**', '*.pdf'), recursive=True)):
        k = pages(p)
        if k:
            rows.append((os.path.relpath(p, B), k))
            tot += k
    for rel, k in rows:
        print('%5d  %s' % (k, rel))
    print('TOTAL pdfs', len(rows), 'pages', tot)
    return 0


if __name__ == '__main__':
    sys.exit(main())
