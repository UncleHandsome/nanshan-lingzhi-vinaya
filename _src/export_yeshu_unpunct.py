# -*- coding: utf-8 -*-
"""匯出業疏仍缺標點的段落（供人工/AI 補標點）。"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷', '03_業疏')
PD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
OUT = os.path.join(B, '業疏標點材料2')
SIZE = 9000


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '標點_*.txt')):
        os.remove(f)
    missing = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        pun = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(PD, ch + '.txt'), encoding='utf-8').read()) if x.strip()]
        for i, (a, b) in enumerate(zip(src, pun)):
            if a == b:
                missing.append((ch, i + 1, a))

    files, buf, cur = [], [], 0
    for ch, seg, text in missing:
        blk = '【%s#%d】\n%s\n\n' % (ch, seg, text)
        if cur + len(blk) > SIZE and buf:
            files.append(buf)
            buf, cur = [], 0
        buf.append(blk)
        cur += len(blk)
    if buf:
        files.append(buf)

    for n, f in enumerate(files, 1):
        head = '# 業疏補標點　第%02d份（共 %d 段）\n# 只加標點，不改字。\n\n' % (n, len(missing))
        io.open(os.path.join(OUT, '標點_%02d.txt' % n), 'w', encoding='utf-8').write(head + ''.join(f))
    print('missing', len(missing), 'files', len(files))
    for f in sorted(glob.glob(os.path.join(OUT, '標點_*.txt'))):
        print(os.path.basename(f), os.path.getsize(f) // 1024, 'KB')


if __name__ == '__main__':
    main()
