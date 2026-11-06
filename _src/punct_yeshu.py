# -*- coding: utf-8 -*-
"""業疏：用分塊句讀檔逐塊取回帶標點的原文（對應分卷段落）"""
import io, os, re, json, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
J = os.path.join(B, 'TXT_句讀', '03_業疏')
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並'}
han_char = lambda c: '\u4e00' <= c <= '\u9fff' or c == '〇'
nh = lambda c: VAR.get(c, c)
hstr = lambda s: ''.join(nh(c) for c in s if han_char(c))
NOISE = re.compile(r'^(=+|（句讀版）|四分律.*卷|\.txt|=====)')


def ju_text_of(key):
    p = os.path.join(J, key + '.txt')
    if not os.path.exists(p):
        return ''
    lines = [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')]
    keep = [x for x in lines if x and not NOISE.match(x) and len(hstr(x)) >= 2]
    return ''.join(keep)


def slice_sp(sp_all, ju_text):
    Sp = ''.join(hstr(x) for x in sp_all)
    Jchars = [c for c in ju_text if han_char(c)]
    Js = ''.join(nh(c) for c in Jchars)
    pos_map = [i for i, c in enumerate(ju_text) if han_char(c)]
    anchors = []
    K, STEP = 16, 8
    for p in range(0, max(0, len(Sp) - K), STEP):
        seg = Sp[p:p + K]
        if len(set(seg)) < 8:
            continue
        q = Js.find(seg)
        if q < 0 or Js.find(seg, q + 1) >= 0:
            continue
        anchors.append((p, q))
    ap = [a[0] for a in anchors]; aq = [a[1] for a in anchors]

    def s2j(pos):
        i = bisect.bisect_right(ap, pos) - 1
        if i < 0:
            return None
        return aq[i] + (pos - ap[i])

    out = []
    start = 0
    for x in sp_all:
        n = len(hstr(x))
        a, b = s2j(start), s2j(start + n - 1)
        start += n
        if a is None or b is None:
            out.append('')
            continue
        i0 = pos_map[a] if a < len(pos_map) else len(ju_text)
        i1 = (pos_map[b] + 1) if b < len(pos_map) else len(ju_text)
        out.append(ju_text[i0:i1].strip())
    return out


allseg = []
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    key = f[:-4]
    sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    jt = ju_text_of(key)
    if not jt:
        allseg += [''] * len(sp)
        continue
    segs = slice_sp(sp, jt)
    ok = sum(1 for x in segs if re.search(r'[，。、；：？！]', x))
    print('%s 段%d 有標點%d' % (key, len(sp), ok))
    allseg += segs

json.dump(allseg, io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json'), 'w', encoding='utf-8'), ensure_ascii=False)
tot = sum(1 for x in allseg if re.search(r'[，。、；：？！]', x))
print('總計', len(allseg), '有標點', tot)
