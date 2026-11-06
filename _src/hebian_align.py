# -*- coding: utf-8 -*-
"""以 n-gram 比對把《資持記》每段錨到《行事鈔》各段，產生對齊表。"""
import io, os, re, json
from bisect import bisect_right

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def load(src, tr):
    S = os.path.join(B, 'TXT_分卷', src)
    T = os.path.join(B, 'AI語譯', 'out', tr)
    out = []
    for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        tp = os.path.join(T, k + '.txt')
        if not os.path.exists(tp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        out.append((k, sp, tt))
    return out


PATS = re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
PATS2 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')

cs = load('01_行事鈔', '01_行事鈔')
secs = []
cur = None
for k, sp, tt in cs:
    vol = k.split('_', 1)[1] if '_' in k else k
    for i in range(len(sp)):
        o = sp[i]
        if PATS2.match(o.strip()):
            continue
        m = PATS.match(o)
        if m:
            if any(x['no'] == m.group(2) for x in secs):
                cur = next(x for x in secs if x['no'] == m.group(2))
            else:
                cur = dict(name=m.group(1), no=m.group(2), items=[])
                secs.append(cur)
            continue
        if cur is not None:
            cur['items'].append((o, tt[i] if i < len(tt) else '', vol))

zj = load('資持記_細分', '資持記')
zflat = []
for k, sp, tt in zj:
    for i in range(len(sp)):
        zflat.append((sp[i], tt[i] if i < len(tt) else ''))
ZP = re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zsecs = []
z = None
for o, t in zflat:
    m = ZP.search(t) or ZP.search(o)
    if m:
        z = dict(name=m.group(1), items=[])
        zsecs.append(z)
    if z is not None:
        z['items'].append((o, t))

MAP = [('標宗顯德', '點明宗旨'), ('集僧通局', '集僧'), ('足數眾相', '足數'), ('受欲是非', '受欲'), ('通辨羯磨', '羯磨'),
       ('結界方法', '結界'), ('僧網大綱', '僧網'), ('受戒緣集', '受戒'), ('師資相攝', '師資'), ('說戒正儀', '說戒'),
       ('安居策修', '安居'), ('自恣宗要', '自恣'), ('篇聚名報', '篇聚'), ('隨戒釋相', '戒相'), ('持犯方軌', '持犯'),
       ('懺六聚法', '懺六聚法'), ('二衣總別', '二衣'), ('四藥受淨', '四藥'), ('鉢器制聽', '鉢器'), ('對施興治', '對施'),
       ('頭陀行儀', '頭陀'), ('僧像致敬', '僧像致敬'), ('訃請設則', '赴請'), ('導俗化方', '導俗'), ('主客相待', '主客'),
       ('瞻病送終', '瞻病'), ('諸雜要行', '諸雜'), ('沙彌別法', '沙彌'), ('尼眾別行', '尼眾'), ('諸部別行', '諸部律')]


def zitems(name):
    out = []
    for s in zsecs:
        if s['name'] == name:
            out += s['items']
    return out


N = 8
result = {}
stats = []
for idx, sec in enumerate(secs):
    zname = MAP[idx][1] if idx < len(MAP) else ''
    zi = zsecs[idx]['items'] if idx < len(zsecs) else []
    ctext = ''
    bounds = []
    for o, t, v in sec['items']:
        bounds.append(len(ctext))
        ctext += han(o)
    bounds.append(len(ctext))
    # 建立 n-gram → 位置索引
    pos = {}
    for i in range(len(ctext) - N + 1):
        pos.setdefault(ctext[i:i + N], []).append(i)
    assigned = []
    hits = 0
    for k, (zo, zt) in enumerate(zi):
        zh = han(zo)
        cand = []
        for i in range(0, max(1, len(zh) - N + 1), max(1, N // 2)):
            g = zh[i:i + N]
            if len(g) < N:
                continue
            for p in pos.get(g, [])[:6]:
                cand.append(p)
        if cand:
            cand.sort()
            p = cand[len(cand) // 2]
            ci = bisect_right(bounds, p) - 1
            ci = max(0, min(len(sec['items']) - 1, ci))
            assigned.append(ci)
            hits += 1
        else:
            assigned.append(None)
    # 單調化 + 內插
    filled = [x for x in assigned if x is not None]
    if filled:
        for k in range(len(assigned)):
            if assigned[k] is None:
                prev = next((assigned[j] for j in range(k - 1, -1, -1) if assigned[j] is not None), None)
                nxt = next((assigned[j] for j in range(k + 1, len(assigned)) if assigned[j] is not None), None)
                if prev is None:
                    assigned[k] = nxt
                elif nxt is None:
                    assigned[k] = prev
                else:
                    frac = (k - [j for j in range(k - 1, -1, -1) if assigned[j] is not None][0]) / \
                           (([j for j in range(k + 1, len(assigned)) if assigned[j] is not None][0]) -
                            ([j for j in range(k - 1, -1, -1) if assigned[j] is not None][0]))
                    assigned[k] = int(round(prev + frac * (nxt - prev)))
        for k in range(1, len(assigned)):
            if assigned[k] < assigned[k - 1]:
                assigned[k] = assigned[k - 1]
    result[str(idx)] = assigned
    stats.append((idx + 1, len(sec['items']), len(zi), hits))

print('篇 | 鈔段 | 記段 | n-gram 命中')
for s in stats:
    print('%3d %5d %5d %5d' % s)
print('命中率 %.1f%%' % (100.0 * sum(s[3] for s in stats) / max(1, sum(s[2] for s in stats))))
json.dump(result, io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('saved hb_align.json')
