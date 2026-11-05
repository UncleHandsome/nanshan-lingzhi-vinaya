import os, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
CLEAN = os.path.join(B, '03_四分律刪補隨機羯磨疏_句讀_clean.txt')
S = os.path.join(B, 'TXT_分卷', '03_業疏')
J = os.path.join(B, 'TXT_句讀', '03_業疏')
TARGETS = ['02b_卷一之二', '03a_卷一之三', '13b_卷三之二', '17a_卷三之六']


def han(s):
    return ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


raw = io.open(CLEAN, encoding='utf-8').read()
chars, idx = [], []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        chars.append(c)
        idx.append(i)
H = ''.join(chars)

for key in TARGETS:
    sp = [x.strip() for x in io.open(os.path.join(S, key + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    h = han(''.join(sp))
    p = -1
    for off in (0, 10, 25, 40, 60):
        probe = h[off:off + 20]
        if len(probe) < 15:
            continue
        p = H.find(probe)
        if p >= 0:
            break
    if p < 0:
        print('!! 仍找不到', key)
        continue
    end = min(len(H) - 1, p + int(len(h) * 1.08))
    seg = raw[idx[p]:idx[end]]
    # 收尾到句號
    k = max(seg.rfind('。'), seg.rfind('！'), seg.rfind('？'))
    if k > len(seg) * 0.6:
        seg = seg[:k + 1]
    lines = [x.strip() for x in seg.split('\n') if x.strip()]
    got = len(han(''.join(lines)))
    print('%-14s p=%d 抽出 %d / 原 %d (%.2f)' % (key, p, got, len(h), got / max(1, len(h))))
    if 0.85 < got / max(1, len(h)) < 1.2:
        io.open(os.path.join(J, key + '.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        print('   written')
