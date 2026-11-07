# -*- coding: utf-8 -*-
"""把 白話/*.docx 轉成同名 PDF（LibreOffice，逐檔獨立 profile，逾時自動放棄）。

用法：
    python _src/mk_pdfs.py                 # 只補「PDF 不存在或比 docx 舊」的
    python _src/mk_pdfs.py --all           # 全部重轉
    python _src/mk_pdfs.py --match 資持記  # 只轉檔名含指定字串的
    python _src/mk_pdfs.py --jobs 4        # 平行 4 個 LibreOffice（預設 1）

要點：
  * 每個檔用獨立的 UserInstallation，避免 LibreOffice 卡在鎖檔。
  * 單檔逾時 240 秒，逾時就殺掉並記錄，不讓整個批次卡住。
  * 轉完檢查 PDF 存在且大於 10KB，否則算失敗。
"""
import os, sys, glob, uuid, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '白話')
SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'


def convert(docx, timeout=240):
    prof = 'file:///C:/Temp/lo_' + uuid.uuid4().hex[:8]
    cmd = [SOFFICE, '--headless', '--norestore', '-env:UserInstallation=' + prof,
           '--convert-to', 'pdf', '--outdir', OUT, docx]
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    pdf = os.path.join(OUT, os.path.splitext(os.path.basename(docx))[0] + '.pdf')
    if os.path.exists(pdf) and os.path.getsize(pdf) > 10000:
        return True, str(os.path.getsize(pdf))
    return False, 'no output'


def main():
    args = sys.argv[1:]
    force = '--all' in args
    match = None
    if '--match' in args:
        match = args[args.index('--match') + 1]
    jobs = 1
    if '--jobs' in args:
        jobs = max(1, int(args[args.index('--jobs') + 1]))

    docxs = sorted(glob.glob(os.path.join(OUT, '*.docx')))
    docxs = [d for d in docxs if not os.path.basename(d).startswith('~$')]
    if match:
        docxs = [d for d in docxs if match in os.path.basename(d)]

    todo = []
    for d in docxs:
        pdf = os.path.splitext(d)[0] + '.pdf'
        if force or not os.path.exists(pdf) or os.path.getmtime(pdf) < os.path.getmtime(d):
            todo.append(d)

    print('待轉 %d / 共 %d（平行 %d）' % (len(todo), len(docxs), jobs))
    ok = fail = 0

    def work(d):
        good, info = convert(d)
        return d, good, info

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = [ex.submit(work, d) for d in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            d, good, info = fut.result()
            print('[%d/%d] %s -> %s (%s)' % (i, len(todo), os.path.basename(d),
                                              'OK' if good else 'FAIL', info), flush=True)
            ok += good
            fail += (not good)
    print('完成：成功 %d，失敗 %d' % (ok, fail))
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
