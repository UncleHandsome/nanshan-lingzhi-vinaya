# -*- coding: utf-8 -*-
"""業疏重譯材料（第二版）：以「分卷＋標點」為底，每檔約 25KB。"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
OUT = os.path.join(B, '業疏重譯2')
SIZE = 8000


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '業疏_*.txt')):
        os.remove(f)
    items = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(f, encoding='utf-8').read()) if x.strip()]
        for i, p in enumerate(ps):
            items.append((ch, i + 1, p))
    files, buf, cur = [], [], 0
    for ch, i, p in items:
        blk = '【%s#%d】\n%s\n\n' % (ch, i, p)
        if cur + len(blk) > SIZE and buf:
            files.append(buf)
            buf, cur = [], 0
        buf.append(blk)
        cur += len(blk)
    if buf:
        files.append(buf)
    for n, f in enumerate(files, 1):
        head = '# 業疏重譯　第%02d批（%d 段）\n# 只譯不改原文，一段對一段，標籤照抄。\n\n' % (n, len(f))
        io.open(os.path.join(OUT, '業疏_%02d.txt' % n), 'w', encoding='utf-8').write(head + ''.join(f))
    print('files', len(files), 'segs', len(items))
    for f in sorted(glob.glob(os.path.join(OUT, '業疏_*.txt'))):
        print(os.path.basename(f), os.path.getsize(f) // 1024, 'KB')


if __name__ == '__main__':
    main()
