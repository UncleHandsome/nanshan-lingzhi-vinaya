# -*- coding: utf-8 -*-
"""產生業疏「偏移表」材料：每個 chunk 邊界的原文尾段與譯文頭尾段。"""
import os, io, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SD = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
TD = os.path.join(B, 'AI語譯', 'out', '03_業疏')
OUT = os.path.join(B, '業疏偏移材料')
SIZE = 9000


def load(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '偏移_*.txt')):
        os.remove(f)
    chunks = []
    for f in sorted(glob.glob(os.path.join(SD, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        chunks.append((ch, load(f), load(os.path.join(TD, ch + '.txt'))))

    blocks = []
    for i in range(len(chunks) - 1):
        ch, src, tr = chunks[i]
        nch, nsrc, ntr = chunks[i + 1]
        L = []
        L.append('## 邊界 %s → %s\n' % (ch, nch))
        L.append('【上一 chunk 原文末 8 段】')
        for j in range(max(0, len(src) - 8), len(src)):
            L.append('（段%d）%s' % (j + 1, src[j]))
        L.append('\n【上一 chunk 譯文末 8 段】')
        for j in range(max(0, len(tr) - 8), len(tr)):
            L.append('（#%d）%s' % (j + 1, tr[j]))
        L.append('\n【下一 chunk 譯文開頭 12 段】')
        for j in range(min(12, len(ntr))):
            L.append('（#%d）%s' % (j + 1, ntr[j]))
        L.append('\n【下一 chunk 原文開頭 3 段】')
        for j in range(min(3, len(nsrc))):
            L.append('（段%d）%s' % (j + 1, nsrc[j]))
        L.append('')
        blocks.append('\n'.join(L))

    files, buf, cur = [], [], 0
    for b in blocks:
        if cur + len(b) > SIZE and buf:
            files.append(buf)
            buf, cur = [], 0
        buf.append(b)
        cur += len(b)
    if buf:
        files.append(buf)

    for n, f in enumerate(files, 1):
        head = '# 業疏偏移表材料　第%02d份\n# 逐個邊界判斷：下一 chunk 開頭有幾段的譯文，其實是上一 chunk 末尾的內容。\n\n' % n
        io.open(os.path.join(OUT, '偏移_%02d.txt' % n), 'w', encoding='utf-8').write(head + '\n'.join(f))
    print('boundaries', len(blocks), 'files', len(files))


if __name__ == '__main__':
    main()
