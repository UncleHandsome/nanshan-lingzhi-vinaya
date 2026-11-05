import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CLEAN = os.path.join(B, '03_四分律刪補隨機羯磨疏_句讀_clean.txt')
S = os.path.join(B, 'TXT_分卷', '03_業疏')
J = os.path.join(B, 'TXT_句讀', '03_業疏')


def han(s):
    return ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


def main(dry=True):
    raw = io.open(CLEAN, encoding='utf-8').read()
    chars, idx = [], []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            chars.append(c)
            idx.append(i)
    H = ''.join(chars)

    chunks = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        chunks.append((f[:-4], han(''.join(sp))))

    pos = 0
    starts = {}
    for key, h in chunks:
        probe = h[:25]
        p = H.find(probe, pos)
        if p < 0:
            p = H.find(h[8:33], pos)
        if p >= 0:
            starts[key] = p
            pos = p + 1

    order = [k for k, _ in chunks]
    out = 0
    for i, key in enumerate(order):
        path = os.path.join(J, key + '.txt')
        if not os.path.exists(path) or os.path.getsize(path) < 60000:
            continue
        p = starts.get(key)
        if p is None:
            print('  跳過(無定位)', key)
            continue
        end = len(H)
        for k2 in order[i + 1:]:
            if k2 in starts:
                end = starts[k2]
                break
        seg = raw[idx[p]:idx[min(end, len(H) - 1)]]
        lines = [x.strip() for x in seg.split('\n') if x.strip()]
        hlen = len(han(''.join(lines)))
        target = dict(chunks)[key]
        ratio = hlen / max(1, len(target))
        print('%-14s 抽出 %6d 字 / 原 %6d (%.2f)' % (key, hlen, len(target), ratio))
        if 0.8 < ratio < 1.25 and not dry:
            io.open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
            out += 1
    print('rewritten', out)


if __name__ == '__main__':
    import sys
    main('--write' not in sys.argv)
