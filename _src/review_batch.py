# -*- coding: utf-8 -*-
"""把每個 chunk 的「原文＋譯文」排成校閱批次檔，供 Review 提示詞逐段使用。

用法：
    python _src/review_batch.py                 # 產生全部 244 個批次
    python _src/review_batch.py --book 資持記   # 只產生某書
    python _src/review_batch.py --chunk 15c_下三 26 38   # 只產生某 chunk 的指定段

輸出：
    AI語譯/_work/review/in/<書>__<chunk>.txt
    AI語譯/_work/review/manifest.tsv

格式（一段對一段）：
    【段001】
    【記】……
    【譯】……
"""
import os, io, re, sys, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WORK = os.path.join(B, 'AI語譯', '_work', 'review')
IN = os.path.join(WORK, 'in')

BOOKS = [
    # out 書名, 分卷目錄, 原文字頭
    ('01_行事鈔', '01_行事鈔', '鈔'),
    ('02_戒疏', '02_戒疏', '疏'),
    ('03_業疏', '03_業疏', '疏'),
    ('資持記', '資持記_細分', '記'),
    ('04_比丘尼鈔', '04_比丘尼鈔', '鈔'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔', '鈔'),
]


def src_paras(path):
    """分卷檔：前 5 行是檔頭，其後每個非空行＝一段。"""
    lines = io.open(path, encoding='utf-8').read().split('\n')[5:]
    return [x.strip() for x in lines if x.strip()]


def tr_paras(path):
    """譯文檔：空行分段。"""
    txt = io.open(path, encoding='utf-8').read()
    return [x.strip() for x in re.split(r'\r?\n\r?\n', txt) if x.strip()]


def make(book, srcdir, tag, chunk, lo=None, hi=None):
    sp = src_paras(os.path.join(B, 'TXT_分卷', srcdir, chunk + '.txt'))
    tp = tr_paras(os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt'))
    if len(sp) != len(tp):
        return None, (len(sp), len(tp))
    n = len(sp)
    a = 1 if lo is None else max(1, lo)
    b = n if hi is None else min(n, hi)
    if a > b:
        return None, ('range', a, b, n)
    out = ['# 校閱批次', '書：%s　chunk：%s　全長：%d 段　本批：%d–%d' % (book, chunk, n, a, b),
           '（段號＝chunk 內第 N 段，空行分段；原文與譯文一段對一段）', '']
    for i in range(a - 1, b):
        out.append('【段%03d】' % (i + 1))
        out.append('【%s】%s' % (tag, sp[i]))
        out.append('【譯】%s' % tp[i])
        out.append('')
    name = '%s__%s' % (book, chunk)
    if lo is not None:
        name += '_%d-%d' % (a, b)
    path = os.path.join(IN, name + '.txt')
    io.open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return path, (n, n, b - a + 1, sum(len(x) for x in sp[a - 1:b]) + sum(len(x) for x in tp[a - 1:b]))


def main():
    args = sys.argv[1:]
    only_book = args[args.index('--book') + 1] if '--book' in args else None
    only_chunk = args[args.index('--chunk') + 1] if '--chunk' in args else None
    os.makedirs(IN, exist_ok=True)
    os.makedirs(os.path.join(WORK, 'out'), exist_ok=True)

    rows = []
    for book, srcdir, tag in BOOKS:
        if only_book and book != only_book:
            continue
        for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', srcdir, '*.txt'))):
            chunk = os.path.splitext(os.path.basename(f))[0]
            if only_chunk and chunk != only_chunk:
                continue
            lo = hi = None
            if only_chunk and len(args) >= 4:
                lo, hi = int(args[2]), int(args[3])
            path, info = make(book, srcdir, tag, chunk, lo, hi)
            if path is None:
                print('!! 段數不符', book, chunk, info)
                continue
            n, _, cnt, chars = info
            rows.append((book, chunk, n, cnt, chars, os.path.basename(path)))
            print('%-10s %-16s 段 %3d  批 %3d  字 %6d' % (book, chunk, n, cnt, chars))

    man = os.path.join(WORK, 'manifest.tsv')
    io.open(man, 'w', encoding='utf-8').write(
        'book\tchunk\tsegs\tbatch_segs\tchars\tfile\n' +
        '\n'.join('\t'.join(map(str, r)) for r in rows) + '\n')
    print('批次', len(rows), '→', man)


if __name__ == '__main__':
    main()
