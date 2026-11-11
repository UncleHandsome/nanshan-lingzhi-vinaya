# -*- coding: utf-8 -*-
"""套用 _mw_edits.py：備份 → 逐筆唯一性替換 → 驗證換行/差異。"""
import io, os, re, sys, shutil, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
BAK = os.path.join(B, '歸檔', '現代詞修正前')
DRY = ('--apply' not in sys.argv)

spec = importlib.util.spec_from_file_location('mw', os.path.join(B, 'AI語譯', '_work', 'review', '_mw_edits.py'))
mw = importlib.util.module_from_spec(spec); spec.loader.exec_module(mw)
EDITS = mw.EDITS

byfile = {}
for i, e in enumerate(EDITS, 1):
    byfile.setdefault((e[0], e[1]), []).append((i, e))

report = []
ok = 0
for (book, f), lst in byfile.items():
    path = os.path.join(OUT, book, f)
    raw = open(path, 'rb').read()
    assert raw[:3] != b'\xef\xbb\xbf', 'BOM: ' + path
    text = raw.decode('utf-8')
    orig = text
    for i, (bk, ff, pidx, old, new) in lst:
        n = text.count(old)
        if n != 1:
            raise SystemExit('edit %d count=%d in %s/%s' % (i, n, book, f))
        text = text.replace(old, new, 1)
        ok += 1
    # 驗證：換行結構不變
    assert text.count('\r') == orig.count('\r'), 'CR mismatch ' + f
    assert text.count('\n') == orig.count('\n'), 'LF mismatch ' + f
    assert len(text) == len(orig) + sum(len(e[4]) - len(e[3]) for _, e in lst)
    if not DRY:
        d = os.path.join(BAK, book)
        os.makedirs(d, exist_ok=True)
        stem, ext = os.path.splitext(f)
        shutil.copyfile(path, os.path.join(d, stem + '_m' + ext))
        with open(path, 'wb') as fh:
            fh.write(text.encode('utf-8'))
    report.append((book, f, len(lst), len(orig), len(text)))

print('DRY' if DRY else 'APPLIED', 'edits', ok, 'files', len(report))
for r in report:
    print('%-8s %-22s %2d 處  %d→%d' % r)
