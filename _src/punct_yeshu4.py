# -*- coding: utf-8 -*-
"""業疏標點（全域）：整本 v3 與分卷原文做字元錨點對齊後切片"""
import io, os, re, json, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
V3 = os.path.join(B, '03_四分律刪補隨機羯磨疏_句讀_v3.txt')
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並',
       '収': '收', '煑': '煮', '査': '查'}
han = lambda c: '\u4e00' <= c <= '\u9fff' or c == '〇'
nh = lambda c: VAR.get(c, c)
hs = lambda s: ''.join(nh(c) for c in s if han(c))


def sim(a, b):
    if not a or not b:
        return 0.0
    n = 6
    sa = {a[i:i + n] for i in range(0, max(1, len(a) - n + 1), 2)}
    sb = {b[i:i + n] for i in range(0, max(1, len(b) - n + 1), 2)}
    return len(sa & sb) / len(sa) if sa else 0.0


sp_all, keys = [], []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    keys.append((k, len(sp)))
    sp_all += sp

t = io.open(V3, encoding='utf-8').read()
i0 = t.find('### 【00_卷首.txt】')
body = t[i0:] if i0 > 0 else t
lines = [x.strip() for x in body.split('\n') if x.strip() and not x.startswith('#') and x.strip() != '---']
jt = ''.join(lines)
Sp, Js = hs(''.join(sp_all)), hs(jt)
print('sp 字', len(Sp), 'ju 字', len(Js))

K, STEP = 16, 8
anchors = []
for p in range(0, max(0, len(Sp) - K), STEP):
    seg = Sp[p:p + K]
    if len(set(seg)) < 8:
        continue
    q = Js.find(seg)
    if q < 0:
        continue
    anchors.append((p, q))
print('錨點', len(anchors))
ap = [a[0] for a in anchors]; aq = [a[1] for a in anchors]
pos_map = [i for i, c in enumerate(jt) if han(c)]


def s2j(p):
    i = bisect.bisect_right(ap, p) - 1
    return aq[i] + (p - ap[i]) if i >= 0 else None


segs = []
start = 0
use = 0
for x in sp_all:
    n = len(hs(x))
    a, b = s2j(start), s2j(start + n - 1)
    start += n
    if a is None or b is None or a >= len(pos_map) or b >= len(pos_map):
        segs.append(x)
        continue
    seg = jt[pos_map[a]:pos_map[b] + 1].strip()
    if re.search(r'[，。、；：？！]', seg) and sim(hs(x), hs(seg)) >= 0.85:
        segs.append(seg)
        use += 1
    else:
        segs.append(x)
print('採用', use, '/', len(segs), '%.1f%%' % (100.0 * use / len(segs)))
json.dump(segs, io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# 每塊統計
gi = 0
bad = []
for k, n in keys:
    seg = segs[gi:gi + n]
    gi += n
    ok = sum(1 for i, s in enumerate(seg) if s != sp_all[gi - n + i])
    if n and ok / n < 0.5:
        bad.append((k, n, ok))
print('低於50%分塊', bad[:8], '共', len(bad))
