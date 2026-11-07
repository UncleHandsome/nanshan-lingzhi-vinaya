# -*- coding: utf-8 -*-
"""把句讀檔的標點投影回分卷（業疏）：輸出不改字、只加標點的分卷。

作法：以段為單位，用段首 8 字在全部句讀檔中定位，再逐字走訪句讀原文，
      遇到同字就收、遇到句讀多出的字（校勘）就跳過、遇到標點就收，
      直到本段漢字全部收完。
"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT_分卷', '03_業疏')
JU = os.path.join(B, 'TXT_句讀', '03_業疏')
OUT = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han_only(s):
    return ''.join(HAN.findall(s))


def load(p, skip):
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[skip:] if x.strip()]


def load_ju():
    books = []
    for f in sorted(glob.glob(os.path.join(JU, '*.txt'))):
        t = '\n'.join(load(f, 4))
        t = re.sub(r'[\r\n\u3000]+', '', t)
        raw = [m.start() for m in HAN.finditer(t)]
        books.append((t, han_only(t), raw))
    return books


def extract(p, hp, books):
    key = hp[:8]
    if len(key) < 4:
        return None
    for t, b, raw in books:
        j = b.find(key)
        if j < 0:
            continue
        i = raw[j]
        pi = 0
        out = []
        while i < len(t) and pi < len(hp):
            ch = t[i]
            if HAN.match(ch):
                if ch == hp[pi]:
                    out.append(ch)
                    pi += 1
            else:
                out.append(ch)
            i += 1
        if pi == len(hp):
            return ''.join(out).strip('，。、；：')
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    books = load_ju()
    total = exact = 0
    report = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = load(f, 5)
        out_paras, ok = [], 0
        for p in src:
            seg = extract(p, han_only(p), books)
            if seg and han_only(seg) == han_only(p):
                out_paras.append(seg)
                ok += 1
            else:
                out_paras.append(p)
        total += len(src)
        exact += ok
        io.open(os.path.join(OUT, ch + '.txt'), 'w', encoding='utf-8').write('\n\n'.join(out_paras) + '\n')
        report.append((ch, len(src), ok, '%.0f%%' % (100.0 * ok / max(1, len(src)))))
    print('paragraphs', total, 'punctuated', exact, '%.1f%%' % (100.0 * exact / max(1, total)))
    for r in report:
        if r[2] < 0.9 * r[1]:
            print('  低', r)


if __name__ == '__main__':
    main()
