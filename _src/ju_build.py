# -*- coding: utf-8 -*-
"""把「句讀原文＋分卷譯文」組成逐段對照（與 build_reflow.py 同一套對位）。

回傳：[(卷名, [(原文段, 譯文), ...]), ...]
"""
import os, io, re, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並'}


def nh(ch):
    return VAR.get(ch, ch)


def ishan(ch):
    return '\u4e00' <= ch <= '\u9fff' or ch == '〇'


def han(s):
    return ''.join(nh(c) for c in s if ishan(c))


def ranges(items):
    starts = []
    off = 0
    hs = []
    for it in items:
        h = han(it)
        hs.append(h)
        starts.append(off)
        off += len(h)
    ends = starts[1:] + [off]
    return ''.join(hs), starts, ends


def anchors(a, b, K=16, STEP=24):
    out = []
    for p in range(0, len(a) - K, STEP):
        seg = a[p:p + K]
        if len(set(seg)) < 7:
            continue
        q = b.find(seg)
        if q < 0:
            continue
        if b.find(seg, q + 1) >= 0:
            continue
        out.append((p, q))
    return out


def load_trs(src_tag, src_dir, tr_tag):
    S = os.path.join(B, 'TXT_分卷', src_dir)
    T = os.path.join(B, 'AI語譯', 'out', tr_tag)
    lines, trs, keys = [], [], []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        tp = os.path.join(T, key + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        for i in range(min(len(sp), len(tt))):
            lines.append(sp[i])
            trs.append(tt[i])
            keys.append(key)
    return lines, trs, keys


def vol_of(key):
    j = key.split('_', 1)[1] if '_' in key else ''
    if j.startswith('卷首'):
        return '卷首'
    m = re.match(r'卷[上中下]', j)
    if m:
        return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j


def build(src_tag, src_dir, tr_tag, ju_file):
    lines, trs, keys = load_trs(src_tag, src_dir, tr_tag)
    src_h, ls, le = ranges(lines)
    raw = io.open(ju_file, encoding='utf-8').read()
    paras = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]
    ju_h, ps, pe = ranges(paras)
    anc = anchors(ju_h, src_h)
    ap = [x[0] for x in anc]
    aq = [x[1] for x in anc]

    def j2s(pos):
        i = bisect.bisect_right(ap, pos) - 1
        if i < 0:
            return max(0, pos)
        return aq[i] + (pos - ap[i])

    out = []
    cur_vol = None
    entries = []
    for pi in range(len(paras)):
        sa = j2s(ps[pi])
        sb = j2s(max(ps[pi] + 1, pe[pi] - 1))
        if sb <= sa:
            sb = sa + 1
        k0 = max(0, bisect.bisect_left(le, sa) - 1)
        got = []
        k = k0
        while k < len(lines) and ls[k] < sb:
            ov = min(le[k], sb) - max(ls[k], sa)
            if ov > 0.5 * (le[k] - ls[k]):
                got.append(k)
            k += 1
        if not got:
            continue
        body = '　'.join(trs[j] for j in got)
        vol = vol_of(keys[got[0]])
        if vol != cur_vol:
            if entries:
                out.append((cur_vol, entries))
            entries = []
            cur_vol = vol
        entries.append((paras[pi], body))
    if entries:
        out.append((cur_vol, entries))
    return out


BOOKS = {
    '03_業疏': ('03_業疏', '03_業疏', os.path.join(B, '03_四分律刪補隨機羯磨疏_句讀_clean.txt')),
    '04_比丘尼鈔': ('04_比丘尼鈔', '04_比丘尼鈔', os.path.join(B, '04_四分律比丘尼鈔_句讀_clean.txt')),
    '05_拾毗尼義鈔': ('05_拾毗尼義鈔', '05_拾毗尼義鈔', os.path.join(B, '05_四分律拾毗尼義鈔_句讀_clean.txt')),
}


if __name__ == '__main__':
    import sys
    tag = sys.argv[1] if len(sys.argv) > 1 else '03_業疏'
    src_dir, tr_tag, ju = BOOKS[tag]
    vols = build(tag, src_dir, tr_tag, ju)
    print('vols', [(v, len(e)) for v, e in vols])
    for v, es in vols[:1]:
        for o, t in es[:4]:
            print('O:', o[:60])
            print('T:', t[:60])
