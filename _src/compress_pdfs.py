# -*- coding: utf-8 -*-
"""用 Ghostscript 壓縮六書 PDF（字型子集化＋串流重壓）。

用法：
  python -X utf8 _src/compress_pdfs.py            # 壓 docs 用的兩個 PDF 目錄
  python -X utf8 _src/compress_pdfs.py --dry      # 只報告預估

預設：-dPDFSETTINGS=/ebook、-dSubsetFonts=true、CompatibilityLevel 1.5
輸出直接覆蓋原檔（先寫 .gs.tmp 再替換）；若壓完反而變大就保留原檔。
"""
import glob
import io
import os
import shutil
import subprocess
import sys
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
GS = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'gs', 'bin', 'gswin64c.exe')
DIRS = [os.path.join(B, '白話對照本_標楷_單欄_PDF'),
        os.path.join(B, '白話對照本_標楷_雙欄_PDF')]


def main():
    dry = '--dry' in sys.argv
    only = []
    for i, a in enumerate(sys.argv):
        if a == '--only' and i + 1 < len(sys.argv):
            only.append(sys.argv[i + 1])
    if not os.path.exists(GS):
        raise SystemExit('找不到 Ghostscript：%s' % GS)
    t0 = time.time()
    before = after = 0
    n = 0
    for d in DIRS:
        if not os.path.isdir(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            if only and not all(x in os.path.basename(p) for x in only):
                continue
            sz = os.path.getsize(p)
            before += sz
            tmp = p + '.gs.tmp'
            r = subprocess.run([GS, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.5',
                                '-dPDFSETTINGS=/ebook', '-dSubsetFonts=true',
                                '-dEmbedAllFonts=true', '-dNOPAUSE', '-dQUIET', '-dBATCH',
                                '-sOutputFile=' + tmp, p],
                               capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(tmp):
                print('跳過（gs 失敗）', os.path.basename(p), r.stderr[:120])
                if os.path.exists(tmp):
                    os.remove(tmp)
                after += sz
                continue
            nsz = os.path.getsize(tmp)
            if nsz < sz * 0.98 and not dry:
                shutil.move(tmp, p)
                print('%-52s %5.1f → %5.1f MB（%.0f%%）'
                      % (os.path.basename(p)[:50], sz / 1048576, nsz / 1048576, nsz * 100.0 / sz))
                after += nsz
            else:
                os.remove(tmp)
                print('%-52s 保持原樣（%.0f%%）' % (os.path.basename(p)[:50], nsz * 100.0 / sz))
                after += sz
            n += 1
    print('\n處理 %d 檔，%.1f MB → %.1f MB（%.0f%%），耗時 %.0f 秒%s'
          % (n, before / 1048576, after / 1048576, after * 100.0 / max(1, before),
             time.time() - t0, '（dry-run 未寫入）' if dry else ''))


if __name__ == '__main__':
    main()
