# -*- coding: utf-8 -*-
"""業疏品質掃描：空譯、長度異常、疑似位移（鄰居譯文更像）"""
import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def grams(s, n=2):
    h = han(s)
    return {h[i:i + n] for i in range(len(h) - n + 1)}

def score(a, b):
    return len(grams(a) & grams(b))

tot = empty = 0
bad_chunks = []
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '03_業疏', '*.txt'))):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '03_業疏', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    n = min(len(sp), len(tt))
    tot += n
    empt = sum(1 for i in range(n) if len(han(tt[i])) < 5)
    empty += empt
    shifty = 0
    for i in range(n - 1):
        s0 = score(sp[i], tt[i])
        s1 = score(sp[i], tt[i + 1])
        if s1 > max(8, s0 * 1.6):
            shifty += 1
    if shifty or empt:
        bad_chunks.append((k, len(sp), len(tt), shifty, empt))
print('總段數', tot, '空譯', empty, '疑似位移段', sum(x[3] for x in bad_chunks))
print('| chunk | 原 | 譯 | 位移 | 空譯 |')
for k, a, b, s, e in bad_chunks:
    print('| %s | %d | %d | %d | %d |' % (k, a, b, s, e))
