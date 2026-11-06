# -*- coding: utf-8 -*-
"""網站用：句讀原文 ↔ 白話 對照。

兩種模式：
  * 分塊模式（業疏）：TXT_句讀/<書>/<分塊>.txt 為該塊的句讀原文，
    以「區塊內」的字元錨點把句讀句分配到分卷行，避免全域漂移。
  * 全書模式（尼鈔、義鈔）：整本 句讀_clean.txt，以 anchors 對到分卷行。

輸出結構：[('卷名', [(原文, 譯文), ...]), ...]
"""
import os, io, re, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並'}


def nh(c):
    return VAR.get(c, c)


def ishan(c):
    return '\u4e00' <= c <= '\u9fff' or c == '〇'


def han(s):
    return ''.join(nh(c) for c in s if ishan(c))


def ranges(items):
    hs, starts, off = [], [], 0
    for it in items:
        h = han(it)
        hs.append(h)
        starts.append(off)
        off += len(h)
    return ''.join(hs), starts, starts[1:] + [off]


def anchors(a, b, K=16, STEP=16):
    out = []
    for p in range(0, max(0, len(a) - K), STEP):
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


def mapper(ju_lines, src_lines):
    jh, js, je = ranges(ju_lines)
    sh, ss, se = ranges(src_lines)
    anc = anchors(jh, sh)
    ap = [x[0] for x in anc]
    aq = [x[1] for x in anc]

    def j2s(pos):
        i = bisect.bisect_right(ap, pos) - 1
        if i < 0:
            return max(0, pos)
        return aq[i] + (pos - ap[i])

    return j2s, js, je, ss, se, len(anc)


def assign(ju_lines, src_lines):
    """把每個句讀句分配到重疊最多的分卷行；回傳每行拼接後的句讀原文。"""
    j2s, js, je, ss, se, nanc = mapper(ju_lines, src_lines)
    buckets = [[] for _ in src_lines]
    for i in range(len(ju_lines)):
        sa = j2s(js[i])
        sb = j2s(max(js[i] + 1, je[i] - 1))
        if sb <= sa:
            sb = sa + 1
        best = None
        bestov = 0
        k = max(0, bisect.bisect_left(se, sa) - 1)
        while k < len(src_lines) and ss[k] < sb:
            ov = min(se[k], sb) - max(ss[k], sa)
            if ov > bestov:
                bestov, best = ov, k
            k += 1
        if best is None:
            best = min(len(src_lines) - 1, max(0, bisect.bisect_right(ss, sa) - 1))
        buckets[best].append(ju_lines[i])
    return buckets, nanc


def vol_of(key):
    j = key.split('_', 1)[1] if '_' in key else ''
    if j.startswith('卷首'):
        return '卷首'
    m = re.match(r'卷[上中下]', j)
    if m:
        return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j


def load_chunks(src_dir, tr_tag):
    S = os.path.join(B, 'TXT_分卷', src_dir)
    T = os.path.join(B, 'AI語譯', 'out', tr_tag)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        tp = os.path.join(T, key + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tt))
    return out


import json as _json
try:
    _AI_YS = _json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align_ys.json'), encoding='utf-8'))
except Exception:
    _AI_YS = {}


TITLE_RE = re.compile(r'^\s*No\.?\s*\d')


def pairs_chunks(src_dir, tr_tag, ju_dir):
    """業疏：句讀原文 ＋ 譯文（譯文開頭多 2 段說明，且原文有標題行無譯）"""
    chunks = load_chunks(src_dir, tr_tag)
    tt_all = []
    for key, sp, tt in chunks:
        tt_all += tt
    res, entries, cur_vol = [], [], None
    core = 0          # 已處理的非標題原文段數
    for key, sp, tt in chunks:
        p = os.path.join(B, 'TXT_句讀', ju_dir, key + '.txt')
        o_lines = None
        if os.path.exists(p):
            ju = [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n') if x.strip()]
            while ju and (len(ju[0]) < 8 or ju[0].startswith(('=', '.', '四分律', '（', '南山三大部', '底本'))):
                ju = ju[1:]
            if ju:
                hs, hd = len(han(''.join(ju))), len(han(''.join(sp)))
                if hd and abs(hs - hd) / hd < 0.30:
                    buckets, _ = assign(ju, sp)
                    o_lines = ['　'.join(b) if b else sp[i] for i, b in enumerate(buckets)]
        if o_lines is None:
            o_lines = sp
        vol = vol_of(key)
        if vol != cur_vol:
            if entries:
                res.append((cur_vol, entries))
            entries, cur_vol = [], vol
        for i in range(len(sp)):
            if TITLE_RE.match(sp[i]):
                continue          # 標題行沒有譯文，不顯示
            g = 2 + core
            t = tt_all[g] if g < len(tt_all) else ''
            entries.append((o_lines[i], t))
            core += 1
    if entries:
        res.append((cur_vol, entries))
    return res


def pairs_global(src_dir, tr_tag, ju_file):
    """尼鈔、義鈔：整本 句讀_clean.txt。"""
    ju = [x.strip() for x in re.split(r'\n\s*\n', io.open(ju_file, encoding='utf-8').read()) if x.strip()]
    src_all, tr_all, keys = [], [], []
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        for i in range(min(len(sp), len(tt))):
            src_all.append(sp[i])
            tr_all.append(tt[i])
            keys.append(key)
    buckets, _ = assign(ju, src_all)
    res = []
    cur_vol = None
    entries = []
    for i, key in enumerate(keys):
        o = '　'.join(buckets[i]) if buckets[i] else src_all[i]
        vol = vol_of(key)
        if vol != cur_vol:
            if entries:
                res.append((cur_vol, entries))
            entries = []
            cur_vol = vol
        entries.append((o, tr_all[i]))
    if entries:
        res.append((cur_vol, entries))
    return res


BOOKS = {
    '03_業疏': dict(src='03_業疏', tr='03_業疏', mode='chunks', ju_dir='03_業疏'),
    '04_比丘尼鈔': dict(src='04_比丘尼鈔', tr='04_比丘尼鈔', mode='global',
                    ju=os.path.join(B, '04_四分律比丘尼鈔_句讀_clean.txt')),
    '05_拾毗尼義鈔': dict(src='05_拾毗尼義鈔', tr='05_拾毗尼義鈔', mode='global',
                     ju=os.path.join(B, '05_四分律拾毗尼義鈔_句讀_clean.txt')),
}


def get(tag):
    cfg = BOOKS[tag]
    if cfg['mode'] == 'chunks':
        return pairs_chunks(cfg['src'], cfg['tr'], cfg['ju_dir'])
    return pairs_global(cfg['src'], cfg['tr'], cfg['ju'])


if __name__ == '__main__':
    import sys
    tag = sys.argv[1] if len(sys.argv) > 1 else '03_業疏'
    vols = get(tag)
    print(tag, [(v, len(e)) for v, e in vols])
    for v, es in vols[:2]:
        for o, t in es[1:4]:
            print('O:', o[:50])
            print('T:', t[:50])
