# -*- coding: utf-8 -*-
"""業疏標點：改用整本 03_..._句讀_v3.txt（按 ### 【分塊】 切段）"""
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


t = io.open(V3, encoding='utf-8').read()
parts = re.split(r'^###\s*【([^】]+)】\s*$', t, flags=re.M)
secs = {}
for i in range(1, len(parts), 2):
    key = parts[i].strip()
    body = parts[i + 1] if i + 1 < len(parts) else ''
    secs[key] = body

print('v3 分塊', len(secs), list(secs)[:5])

allseg = []
stat = {}
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    body = secs.get(key + '.txt', '')
    if not body:
        allseg += sp
        stat[key] = (len(sp), 0)
        continue
    lines = [x.strip() for x in body.split('\n') if x.strip() and not x.startswith('#') and x.strip() != '---']
    jt = ''.join(lines)
    Sp, Js = hs(''.join(sp)), hs(jt)
    K, STEP = 16, 8
    anchors = []
    for p in range(0, max(0, len(Sp) - K), STEP):
        seg = Sp[p:p + K]
        if len(set(seg)) < 8:
            continue
        q = Js.find(seg)
        if q < 0 or Js.find(seg, q + 1) >= 0:
            continue
        anchors.append((p, q))
    ap = [a[0] for a in anchors]; aq = [a[1] for a in anchors]
    pos_map = [i for i, c in enumerate(jt) if han(c)]

    def s2j(pos):
        i = bisect.bisect_right(ap, pos) - 1
        return aq[i] + (pos - ap[i]) if i >= 0 else None

    segs = []
    start = 0
    for x in sp:
        n = len(hs(x))
        a, b = s2j(start), s2j(start + n - 1)
        start += n
        if a is None or b is None or a >= len(pos_map) or b >= len(pos_map):
            segs.append(x)
            continue
        seg = jt[pos_map[a]:pos_map[b] + 1].strip()
        if re.search(r'[，。、；：？！]', seg) and sim(hs(x), hs(seg)) >= 0.85:
            segs.append(seg)
        else:
            segs.append(x)
    ok = sum(1 for i, s in enumerate(segs) if s != sp[i])
    stat[key] = (len(sp), ok)
    allseg += segs

json.dump(allseg, io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json'), 'w', encoding='utf-8'), ensure_ascii=False)
tot = sum(1 for x in allseg if re.search(r'[，。、；：？！]', x))
print('總段', len(allseg), '採用標點', tot, '%.1f%%' % (100.0 * tot / len(allseg)))
low = [(k, v) for k, v in stat.items() if v[0] and v[1] / v[0] < 0.5]
print('低採用分塊', len(low), low[:8])
