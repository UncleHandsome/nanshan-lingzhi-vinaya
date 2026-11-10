# -*- coding: utf-8 -*-
"""網站用：句讀原文 ↔ 白話 對照。

兩種模式：
  * 分塊模式（業疏）：TXT_句讀/<書>/<分塊>.txt 為該塊的句讀原文，
    以「區塊內」的字元錨點把句讀句分配到分卷行，避免全域漂移。
  * 全書模式（尼鈔、義鈔）：整本 句讀_clean.txt，以 anchors 對到分卷行。

輸出結構：[('卷名', [(原文, 譯文), ...]), ...]
"""
import os, io, re, glob, bisect, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並'}


def _ju_path(B, name):
    """句讀_clean 檔可能被歸檔到 歸檔/臨時檔/，兩處都找。"""
    for rel in ('', os.path.join('歸檔', '臨時檔')):
        p = os.path.join(B, rel, name) if rel else os.path.join(B, name)
        if os.path.exists(p):
            return p
    return os.path.join(B, name)

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
try:
    _YS_OFF = _json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets_final.json'), encoding='utf-8'))
except Exception:
    _YS_OFF = {}
try:
    _YS_MAP = _json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json'), encoding='utf-8'))
except Exception:
    _YS_MAP = {}
try:
    _YS_JU = _json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'ys_ju_map.json'), encoding='utf-8'))
except Exception:
    _YS_JU = {}

# 卷首的人工修正（ye_new.txt 指定的 3~5 列）
_YS0_FIX = {
    2: '【篇名題署】No. 728-B 會刻羯磨疏記序',
    3: '曾聽聞毗尼律藏乃是佛法長久傳續的真實壽命；律藏若能久住於世，正法才得依託久住。因此，生長一切善法、滅除一切罪惡，全以如法羯磨為其宗要；斷盡妄見惑障、證悟涅槃聖理，沒有比受戒之體更重要的了；滅除罪惡之大，沒有比懺悔重罪更高的了。羯磨的功德，其深遠可知。',
    4: '時值享保十五年、歲次庚戌（龍舍）秋季七月十五僧自恣日，通受戒苾芻禪龍於泉州萬代莊佛頂山金輪寺丈室敬謹書寫。',
}


def _off_for(off, i):
    """off 可為整數或 [[起,迄,位移],...]"""
    if isinstance(off, (int, float)):
        return int(off)
    for a, b, o in off:
        if a <= i <= b:
            return int(o)
    return 0


def pairs_chunks(src_dir, tr_tag, ju_dir):
    """業疏：句讀原文 ＋ 全域譯文流（逐塊位移，可正可負）"""
    chunks = load_chunks(src_dir, tr_tag)
    tt_all, pref = [], {}
    for key, sp, tt in chunks:
        pref[key] = len(tt_all)
        tt_all += tt
    res, entries, cur_vol = [], [], None
    for key, sp, tt in chunks:
        off = _YS_OFF.get(key, 0)
        p = os.path.join(B, 'TXT_句讀', ju_dir, key + '.txt')
        o_lines = None
        if os.path.exists(p):
            ju = [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n') if x.strip()]
            while ju and (len(ju[0]) < 8 or ju[0].startswith(('=', '.', '四分律', '（', '南山三大部', '底本'))):
                ju = ju[1:]
            if ju:
                rec = _YS_JU.get(key)
                jm = rec.get('map') if isinstance(rec, dict) else rec
                if isinstance(rec, dict):
                    t0 = int(rec.get('trim', 0))
                    if t0:
                        ju = ju[t0:]
                if jm and len(jm) == len(ju):
                    buck = [[] for _ in sp]
                    for li, si in enumerate(jm):
                        if 0 <= si < len(buck):
                            buck[si].append(ju[li])
                    o_lines = ['　'.join(b) if b else sp[i] for i, b in enumerate(buck)]
                else:
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
        mp = _YS_MAP.get(key)
        for i in range(len(sp)):
            if TITLE_RE.match(sp[i]):
                continue
            if mp and i < len(mp):
                g = pref[key] + int(mp[i])
            else:
                g = pref[key] + i + _off_for(off, i)
            t = tt_all[g] if 0 <= g < len(tt_all) else ''
            if key.startswith('00_卷首') and i in _YS0_FIX:
                t = _YS0_FIX[i]
            entries.append((o_lines[i], t))
    if entries:
        res.append((cur_vol, entries))
    return res


PUNCT_MAPS = {'04_比丘尼鈔': 'nicao_punct.json', '05_拾毗尼義鈔': 'yichao_punct.json'}


def pairs_global(src_dir, tr_tag, ju_file):
    """尼鈔、義鈔：整本 句讀_clean.txt（優先使用字元錨點取回的帶標點段落）。"""
    ju = [x.strip() for x in re.split(r'\n\s*\n', io.open(ju_file, encoding='utf-8').read()) if x.strip()]
    src_all, tr_all, keys = [], [], []
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        for i in range(min(len(sp), len(tt))):
            src_all.append(sp[i])
            tr_all.append(tt[i])
            keys.append(key)
    punct = None
    pm = PUNCT_MAPS.get(src_dir)
    if pm:
        pth = os.path.join(B, 'AI語譯', '_work', pm)
        if os.path.exists(pth):
            punct = json.load(io.open(pth, encoding='utf-8'))
    buckets, _ = assign(ju, src_all)
    res = []
    cur_vol = None
    entries = []
    for i, key in enumerate(keys):
        o = '　'.join(buckets[i]) if buckets[i] else src_all[i]
        if punct and i < len(punct) and re.search(r'[，。、；：？！」]', punct[i]):
            o = punct[i]
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
    '03_業疏': dict(src='03_業疏', tr='03_業疏', mode='simple'),
    '04_比丘尼鈔': dict(src='04_比丘尼鈔', tr='04_比丘尼鈔', mode='global',
                    ju=_ju_path(B, '04_四分律比丘尼鈔_句讀_clean.txt')),
    '05_拾毗尼義鈔': dict(src='05_拾毗尼義鈔', tr='05_拾毗尼義鈔', mode='global',
                     ju=_ju_path(B, '05_四分律拾毗尼義鈔_句讀_clean.txt')),
}


def pairs_simple(src_dir, tr_tag):
    """直接以分卷原文配白話（段數已 1:1），有標點表則優先使用。"""
    punct = None
    pth = os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json')
    if os.path.exists(pth):
        punct = json.load(io.open(pth, encoding='utf-8'))
    ytags = None
    pth3 = os.path.join(B, 'AI語譯', '_work', 'yeshu_tags.json')
    if os.path.exists(pth3):
        ytags = json.load(io.open(pth3, encoding='utf-8'))
    amap = None
    pth2 = os.path.join(B, 'AI語譯', '_work', 'ys_align_map.json')
    if os.path.exists(pth2):
        amap = json.load(io.open(pth2, encoding='utf-8'))
    res = []
    cur = None
    entries = []
    gi = -1
    for key, sp, tt in load_chunks(src_dir, tr_tag):
        vol = vol_of(key)
        if vol != cur:
            if entries:
                res.append((cur, entries))
            entries = []
            cur = vol
        n = min(len(sp), len(tt))
        mp = amap.get(key) if (amap and not key.startswith('00_')) else None
        for i in range(n):
            gi += 1
            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
            o = o.strip('*').lstrip()
            o = re.sub(r'\*+', '', o)
            m3 = re.search(r'【[疏記]】', o)
            if m3 and m3.start() > 0:
                o = o[m3.start():]
            if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):
                o = ytags[gi] + o
            j = i
            if mp and i < len(mp) and 0 <= mp[i] < len(tt):
                j = mp[i]
            entries.append((o, tt[j]))
        for i in range(n, len(sp)):
            gi += 1
            entries.append((sp[i], ''))
    if entries:
        res.append((cur, entries))
    return res


def _yeshu_direct():
    """業疏：優先讀 ys_pairs_fixed.json（已修正 chunk 旋轉位移），否則用分卷＋標點 1:1。"""
    fp = os.path.join(B, 'AI語譯', '_work', 'ys_pairs_fixed.json')
    vols = {}
    if os.path.exists(fp):
        data = _json.load(io.open(fp, encoding='utf-8'))
        for ch, pairs in data.items():
            vol = ch.split('_')[1][:2] if '_' in ch else '卷首'
            vols.setdefault(vol, []).extend([(s, t) for s, t in pairs])
        order = ['卷首', '卷一', '卷二', '卷三', '卷四']
        return [(v, vols[v]) for v in order if vols.get(v)]

    sd = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
    td = os.path.join(B, 'AI語譯', 'out', '03_業疏')
    vols = {}
    for f in sorted(glob.glob(os.path.join(sd, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        vol = ch.split('_')[1][:2]          # 卷一 / 卷二 / 卷三 / 卷四 / 卷首
        if vol == '卷首':
            vol = '卷首'
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n') if x.strip()]
        tp = os.path.join(td, ch + '.txt')
        if not os.path.exists(tp):
            continue
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        pairs = list(zip(src, tr))
        vols.setdefault(vol, []).extend(pairs)
    order = ['卷首', '卷一', '卷二', '卷三', '卷四']
    return [(v, vols[v]) for v in order if vols.get(v)]


def get(tag):
    if tag == '03_業疏' and os.path.isdir(os.path.join(B, 'TXT_分卷_標點', '03_業疏')):
        return _yeshu_direct()
    cfg = BOOKS[tag]
    if cfg['mode'] == 'simple':
        return pairs_simple(cfg['src'], cfg['tr'])
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
