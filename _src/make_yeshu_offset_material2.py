# -*- coding: utf-8 -*-
"""業疏偏移表材料 v2：給「上一 chunk 最後 3 段原文」＋「下一 chunk 全部譯文」，用搜尋定位。

每個邊界問一題：上一 chunk 最後一段的譯文，是下一 chunk 的第幾段（p）？
p 就是下一 chunk 的 k（開頭有幾段屬於上一 chunk）。
"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
TD = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, '業疏偏移材料2')


def load(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '偏移2_*.txt')):
        os.remove(f)
    chunks = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        chunks.append((ch, load(f), load(os.path.join(TD, ch + '.txt'))))

    blocks = []
    for i in range(len(chunks) - 1):
        ch, src, tr = chunks[i]
        nch, nsrc, ntr = chunks[i + 1]
        L = ['## 邊界 %s → %s\n' % (ch, nch)]
        L.append('【上一 chunk 最後 3 段原文】')
        for j in range(max(0, len(src) - 3), len(src)):
            L.append('（段%d）%s' % (j + 1, src[j]))
        L.append('\n【下一 chunk 全部譯文】（共 %d 段）' % len(ntr))
        for j, t in enumerate(ntr):
            L.append('（#%d）%s' % (j + 1, t))
        L.append('\n問題：上一 chunk 最後一段（段%d）的譯文，是下一 chunk 的第幾段？\n' % len(src))
        blocks.append('\n'.join(L))

    total = sum(len(b) for b in blocks)
    half = total / 2
    files, buf, cur = [], [], 0
    for b in blocks:
        if cur + len(b) > half and len(files) == 0:
            files.append(buf)
            buf, cur = [], 0
        buf.append(b)
        cur += len(b)
    if buf:
        files.append(buf)

    for n, f in enumerate(files, 1):
        head = ('# 業疏偏移表材料 v2　第%d份（共 %d 個邊界）\n'
                '# 每題：在下一 chunk 的全部譯文中，找出上一 chunk 最後一段的譯文。\n\n') % (n, len(blocks))
        io.open(os.path.join(OUT, '偏移2_%02d.txt' % n), 'w', encoding='utf-8').write(head + '\n'.join(f))

    print('boundaries', len(blocks), 'files', len(files), 'total chars', total)
    for f in sorted(glob.glob(os.path.join(OUT, '偏移2_*.txt'))):
        print(os.path.basename(f), os.path.getsize(f) // 1024, 'KB')


if __name__ == '__main__':
    main()
