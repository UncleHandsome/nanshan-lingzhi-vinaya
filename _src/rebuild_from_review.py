# -*- coding: utf-8 -*-
"""校閱修正後的一次性重建：會本 → 各書 docx → 合編 → 網站 → PDF。

用法：
    python _src/rebuild_from_review.py            # 全部
    python _src/rebuild_from_review.py --no-pdf   # 略過 PDF
"""
import os, sys, subprocess, time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable


def run(args, label):
    t0 = time.time()
    print('>>', label, flush=True)
    r = subprocess.run([PY, '-X', 'utf8'] + args, cwd=B, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    ok = r.returncode == 0
    tail = (r.stdout or '').strip().split('\n')[-3:]
    print('\n'.join(tail), flush=True)
    if not ok:
        print('!! FAILED', label, (r.stderr or '')[-500:], flush=True)
    print('   %.1fs' % (time.time() - t0), flush=True)
    return ok


def main():
    no_pdf = '--no-pdf' in sys.argv
    steps = []
    pian = [str(i) for i in range(1, 31) if i != 6]
    steps.append((['_src/mk_pian_split.py'] + pian, '會本 30 篇'))
    steps.append((['_src/build_vol.py'], '行事鈔三卷'))
    steps.append((['_src/build_ju_vol.py', '--no-pdf'], '業疏/尼鈔/尼義鈔 docx'))
    steps.append((['_src/build_book.py', '02_戒疏', '四分律含注戒本疏', '戒疏', '02_戒疏'], '戒疏八卷'))
    steps.append((['_src/build_book.py', '資持記', '四分律行事鈔資持記', '資持記', '資持記_細分'], '資持記十六卷'))
    steps.append((['_src/rebuild_hebian_v2.py'], '合編 12 卷 docx'))
    steps.append((['_src/site_hebian.py'], '合編網站'))
    steps.append((['_src/site2.py'], '全站'))
    if not no_pdf:
        steps.append((['_src/mk_pdfs.py', '--jobs', '4'], 'PDF 全轉'))

    bad = []
    for args, label in steps:
        if not run(args, label):
            bad.append(label)
    print('DONE; failed:', bad if bad else 'none')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
