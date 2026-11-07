# -*- coding: utf-8 -*-
"""產生業疏重譯材料：每檔約 25KB（UTF-8），只給原文與段號。"""
import os, io, re, glob, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '業疏重譯')
SRC = os.path.join(B, 'TXT_分卷', '03_業疏')
SIZE = 25000
if '--size' in sys.argv:
    SIZE = int(sys.argv[sys.argv.index('--size') + 1])


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.txt')):
        os.remove(f)
    rows, buf, cur, seg = [], [], 0, 0
    n = 0
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        ps = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        for i, p in enumerate(ps):
            block = '【段%04d】03_業疏/%s#%d\n【原文】%s\n\n' % (seg + 1, ch, i + 1, p)
            b = len(block.encode('utf-8'))
            if cur + b > SIZE and buf:
                n += 1
                name = '業疏_%02d.txt' % n
                head = '# 業疏重譯　第%d批（段%d–%d）\n\n' % (n, 1, seg)
                io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(head + ''.join(buf))
                rows.append((name, seg, cur))
                buf, cur, seg = [], 0, 0
            seg += 1
            buf.append(block)
            cur += b
    if buf:
        n += 1
        name = '業疏_%02d.txt' % n
        head = '# 業疏重譯　第%d批（段%d–%d）\n\n' % (n, 1, seg)
        io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(head + ''.join(buf))
        rows.append((name, seg, cur))
    with io.open(os.path.join(OUT, 'index.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('file\tsegs\tbytes\n')
        for r in rows:
            fh.write('%s\t%d\t%d\n' % r)
    print('files', len(rows), 'segs', seg)
    for r in rows[:5]:
        print(r)


if __name__ == '__main__':
    main()
