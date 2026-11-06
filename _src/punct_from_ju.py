# -*- coding: utf-8 -*-
"""用整本句讀檔的字元錨點，為每個分卷段落取回帶標點的文字"""
import io, os, re, json, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並'}
han_char = lambda c: '\u4e00' <= c <= '\u9fff' or c == '〇'
nh = lambda c: VAR.get(c, c)
hstr = lambda s: ''.join(nh(c) for c in s if han_char(c))


def build(sp_all, ju_text):
    Sp = ''.join(hstr(x) for x in sp_all)
    # ju：保留原字串，同時建立 han→原字元位置對照
    Jchars = [c for c in ju_text if han_char(c)]
    J = ''.join(nh(c) for c in Jchars)
    # 原字元位置
    pos_map = [i for i, c in enumerate(ju_text) if han_char(c)]
    # 錨點：16 字唯一片段
    anchors = []
    K, STEP = 16, 8
    for p in range(0, max(0, len(Sp) - K), STEP):
        seg = Sp[p:p + K]
        if len(set(seg)) < 8:
            continue
        q = J.find(seg)
        if q < 0 or J.find(seg, q + 1) >= 0:
            continue
        anchors.append((p, q))
    ap = [a[0] for a in anchors]
    aq = [a[1] for a in anchors]

    def s2j(pos):
        i = bisect.bisect_right(ap, pos) - 1
        if i < 0:
            return 0
        return aq[i] + (pos - ap[i])

    out = []
    start = 0
    for x in sp_all:
        n = len(hstr(x))
        a = s2j(start)
        b = s2j(start + n - 1) + 1
        start += n
        # 轉回 ju 原字元
        i0 = pos_map[a] if a < len(pos_map) else len(ju_text)
        i1 = (pos_map[b - 1] + 1) if 0 <= b - 1 < len(pos_map) else len(ju_text)
        seg = ju_text[i0:i1].strip()
        out.append(seg)
    return out, len(anchors)


TARGETS = [('04_比丘尼鈔', '04_四分律比丘尼鈔_句讀_clean.txt', 'nicao_punct.json'),
           ('05_拾毗尼義鈔', '05_四分律拾毗尼義鈔_句讀_clean.txt', 'yichao_punct.json')]
for src, jufile, out in TARGETS:
    S = os.path.join(B, 'TXT_分卷', src)
    sp_all = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        sp_all += sp
    ju_text = io.open(os.path.join(B, jufile), encoding='utf-8').read()
    segs, na = build(sp_all, ju_text)
    punct = sum(1 for s in segs if re.search(r'[，。、；：？！]', s))
    json.dump(segs, io.open(os.path.join(B, 'AI語譯', '_work', out), 'w', encoding='utf-8'), ensure_ascii=False)
    print('%s 段%d 有標點%d (%.0f%%) 錨點%d' % (src, len(segs), punct, 100.0 * punct / len(segs), na))
