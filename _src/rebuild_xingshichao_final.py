# -*- coding: utf-8 -*-
"""行事鈔定稿重建（小單位，不用長段大單位）。

來源：
  _終審/<n>.md          …… 原文來源 + 待審譯文（PASS 用）
  _終修/回覆/<n>_回.txt …… 修訂後譯文（FIX 用；定稿若未套用時優先）
  _定稿/<n>.txt         …… 定稿譯文（優先）
  TXT/01_四分律刪繁補闕行事鈔.txt …… 原文權威
缺口補法：docs/xingshichao 頁面「小 pair」逐 pair 補（只讀 HTML，不修改）。

輸出：定稿/xingshichao.jsonl（舊檔先備份為 定稿/_舊_xingshichao.jsonl）
"""
import io, json, os, re, shutil, html, difflib, sys
DRY = '--dry' in sys.argv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '行事鈔')
td = os.path.join(ROOT, '_終審')
rev = os.path.join(ROOT, '_終修', '回覆')
fin = os.path.join(ROOT, '_定稿')
RAW = io.open(os.path.join(B, 'TXT', '01_四分律刪繁補闕行事鈔.txt'), encoding='utf-8').read()
H = ''.join(re.findall(r'[\u4e00-\u9fff]', RAW))
MP = [i for i, c in enumerate(RAW) if '\u4e00' <= c <= '\u9fff']
LAB = re.compile(r'^【[^】]{1,8}】\s*')
LABFULL = re.compile(r'^【[^】]{1,8}】$')
STAT = {}

def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def source_block(md):
    m = re.search(r'■\s*([^\n（■]*?)（原文）', md)
    if not m:
        return '', ''
    label = m.group(1).strip()
    s = md[m.end():]
    cut = re.search(r'\n\s*■\s*[^\n（]*（|【待審譯文】|【裁決|【後文背景|\n\s*---', s)
    if cut:
        s = s[:cut.start()]
    return label, s.strip()

def trans_of(md):
    j = md.rfind('【待審譯文】')
    if j < 0:
        return ''
    s = md[j + len('【待審譯文】'):]
    cut = re.search(r'【後文背景|【裁決|\n\s*---', s)
    if cut:
        s = s[:cut.start()]
    return s.strip()

def clean(tr):
    tr = tr.strip()
    tr = re.sub(r'^】+\s*', '', tr)
    lines = [x for x in tr.splitlines() if x.strip()]
    while lines:
        if LABFULL.match(lines[0]):
            lines = lines[1:]
            continue
        m = LAB.match(lines[0])
        if m:
            rest = lines[0][m.end():].strip()
            if rest:
                lines[0] = rest
            else:
                lines = lines[1:]
        break
    return '\n'.join(lines).strip()

def chunk_of(md):
    m = re.search(r'出處：\s*([0-9]{2}[a-d])_([^\s，,]+)', md)
    return (m.group(1), m.group(2)) if m else ('', '')

def raw_slice(a, b):
    """han 索引區間 → 原文（含標點）。"""
    if a < 0 or b <= a:
        return ''
    return RAW[MP[a]:MP[b - 1] + 1].strip()

OPENERS = '《「『（〈【〔'
CLOSERS = '。！？》」』）〉】〕'

def raw_slice_padded(a, b):
    """docs pair 用：把緊鄰的開引號／收尾標點一併納入，避免 source 從『》』或半個書名號開始。"""
    if a < 0 or b <= a:
        return ''
    s = MP[a]
    e = MP[b - 1] + 1
    if s > 0 and RAW[s - 1] in OPENERS:
        s -= 1
    if e < len(RAW) and RAW[e] in CLOSERS:
        e += 1
    return RAW[s:e].strip()

# ---------- 卷界 ----------
CHUNKS = [('卷上之一', '四分律刪繁補闕行事鈔卷上之一'), ('卷上之二', '四分律刪繁補闕行事鈔卷上之二'),
          ('卷上之三', '四分律刪繁補闕行事鈔卷上之三'), ('卷上之四', '四分律刪繁補闕行事鈔卷上之四'),
          ('卷中之一', '四分律刪繁補闕行事鈔卷中之一'), ('卷中之二', '四分律刪繁補闕行事鈔卷中之二'),
          ('卷中之三', '四分律刪繁補闕行事鈔卷中之三'), ('卷中之四', '四分律刪繁補闕行事鈔卷中之四'),
          ('卷下之一', '四分律刪繁補闕行事鈔卷下之一'), ('卷下之二', '四分律刪繁補闕行事鈔卷下之二'),
          ('卷下之三', '四分律刪繁補闕行事鈔卷下之三'), ('卷下之四', '四分律刪繁補闕行事鈔卷下之四')]
BOUND = []
for name, title in CHUNKS:
    p = H.find(title)
    if p < 0:
        raise SystemExit('卷題找不到：' + title)
    BOUND.append((p, name))
BOUND.sort()
STAT['卷界'] = BOUND
STAT['卷界數'] = len(BOUND)

def chunk_at(x):
    name = BOUND[0][1]
    for p, nm in BOUND:
        if x >= p:
            name = nm
    return name

# ---------- docs 小 pair ----------
pairs = []
for vol in ('卷上', '卷中', '卷下'):
    t = io.open(os.path.join(B, 'docs', 'xingshichao', vol + '.html'), encoding='utf-8').read()
    for m in re.finditer(r'<div class="pair[^"]*"><div class="o[^"]*">(.*?)</div><div class="t">(.*?)</div></div>', t, re.S):
        o = html.unescape(re.sub('<[^>]+>', '', m.group(1)))
        tr = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        pairs.append({'vol': vol, 'o': o, 'tr': tr.strip(), 's': han(o), 'q': -1, 'e': -1, 'used': False})
pos = 0
clipped = []
for p in pairs:
    s = p['s']
    q = -1
    for n in (20, 12, 8, 4):
        if len(s) >= n:
            q = H.find(s[:n], pos)
            if q >= 0:
                break
    if q < 0:
        q = H.find(s, pos)
    if q < 0:
        # 前一個 pair 多吃掉開頭幾字時，允許向前回溯（把重疊部分裁掉）
        st = max(0, pos - 16)
        for n in (20, 12, 8, 4):
            if len(s) < n:
                continue
            q2 = H.find(s[:n], st)
            if st <= q2 < pos:
                clipped.append((p['vol'], q2, pos, pos, q2 + len(s), p['o'][:40]))
                p['q'] = pos
                p['e'] = q2 + len(s)
                pos = p['e']
                break
        if p['q'] >= 0:
            continue
    p['q'] = q
    p['e'] = q + len(s) if q >= 0 else -1
    if q >= 0:
        pos = p['e']
STAT['docs_pair_裁切'] = clipped
STAT['docs_pair'] = len(pairs)
STAT['docs_pair_未定位'] = sum(1 for p in pairs if p['q'] < 0)
PSTART = {p['q']: i for i, p in enumerate(pairs) if p['q'] >= 0}
PEND = {p['e']: i for i, p in enumerate(pairs) if p['e'] >= 0}

# ---------- 終審骨幹 ----------
mdfiles = {int(f[:-3]): f[:-3] for f in os.listdir(td) if f.endswith('.md')}
finfiles = {int(f[:-4]): f[:-4] for f in os.listdir(fin) if f.endswith('.txt')}
revfiles = {int(f[:-6]): f[:-6] for f in os.listdir(rev) if f.endswith('_回.txt')}
alln = sorted(set(mdfiles) | set(finfiles))
units = []
for n in alln:
    key = mdfiles.get(n) or finfiles.get(n) or str(n)
    u = {'n': n, 'key': key, 'label': '鈔文', 'src': '', 'trial': '', 'fin': '', 'rev': '',
         'code': '', 'chunk': '', 'origin': '', 'q': -1, 'e': -1, 'tr': '', 'revised': False}
    if n in mdfiles:
        md = io.open(os.path.join(td, key + '.md'), encoding='utf-8').read()
        lab, src = source_block(md)
        u['label'] = lab or '鈔文'
        u['src'] = src
        u['trial'] = clean(trans_of(md))
        u['code'], u['chunk'] = chunk_of(md)
        u['origin'] = '終審'
    if n in finfiles:
        u['fin'] = clean(io.open(os.path.join(fin, key + '.txt'), encoding='utf-8').read())
    if n in revfiles:
        u['rev'] = clean(io.open(os.path.join(rev, key + '_回.txt'), encoding='utf-8').read())
    # 譯文選擇：定稿優先；定稿仍等於待審而回覆不同 → 回覆（修訂未套用）
    if u['fin'] and (u['fin'] != u['trial'] or not u['rev']):
        u['tr'], u['picksrc'] = u['fin'], '定稿'
    elif u['rev']:
        u['tr'], u['picksrc'] = u['rev'], '回覆'
    else:
        u['tr'], u['picksrc'] = u['fin'] or u['trial'], '待審'
    u['revised'] = bool(u['tr']) and bool(u['trial']) and (re.sub(r'\s+', '', u['tr']) != re.sub(r'\s+', '', u['trial']))
    units.append(u)
STAT['骨幹單位'] = len(units)
STAT['終審md'] = len(mdfiles)
STAT['譯文來源'] = {}
for u in units:
    STAT['譯文來源'][u['picksrc']] = STAT['譯文來源'].get(u['picksrc'], 0) + 1

# ---------- 定位（順序前綴比對）----------
pos = 0
nf = []
for u in units:
    s = han(u['src'])
    if not s:
        continue
    q = -1
    for ln in (20, 12, 8):
        if len(s) >= ln:
            q = H.find(s[:ln], pos)
            if q >= 0:
                break
    if q < 0 and len(s) >= 4:
        q = H.find(s[:4], pos)
    if q < 0:
        q = H.find(s, pos)
    if q < 0:
        nf.append(u['key'])
        continue
    u['q'] = q
    u['e'] = q + len(s)
    pos = max(pos, u['e'])

# ---------- 37 個只有定稿、無終審原文的單位：用 docs pair 譯文相似度取回原文區間 ----------
def norm(s):
    return re.sub(r'[^\u4e00-\u9fff]', '', s)

orph = [u for u in units if u['q'] < 0]
STAT['無原文單位'] = len(orph)
orph_fix = []
for u in orph:
    best = None
    for p in pairs:
        if p['q'] < 0 or p['used']:
            continue
        r = difflib.SequenceMatcher(None, norm(u['tr']), norm(p['tr'])).ratio()
        if best is None or r > best[0]:
            best = (r, p)
    if best and best[0] >= 0.90:
        p = best[1]
        u['q'], u['e'] = p['q'], p['e']
        u['src'] = raw_slice_padded(p['q'], p['e'])
        u['origin'] = '定稿（原文區間由 docs pair 譯文比對取得）'
        u['chunk'] = u['chunk'] or chunk_at(p['q'])
        p['used'] = True
        orph_fix.append((u['key'], round(best[0], 3), p['q'], p['e']))
    else:
        u['e'] = -1
STAT['孤兒取回原文'] = len(orph_fix)
STAT['孤兒取回明細'] = orph_fix
STAT['孤兒未取回'] = [u['key'] for u in orph if u['q'] < 0]

# ---------- 骨幹單位對應 docs pair ----------
miss_align = []
for u in units:
    if u['q'] < 0:
        continue
    if u['q'] not in PSTART or u['e'] not in PEND:
        miss_align.append((u['key'], u['q'], u['e']))
    else:
        i, j = PSTART[u['q']], PEND[u['e']]
        for k in range(i, j + 1):
            pairs[k]['used'] = True
STAT['骨幹未對齊pair邊界'] = len(miss_align)
STAT['骨幹未對齊樣本'] = miss_align[:10]

# ---------- 補：未被骨幹認領的 pair → 小單位 ----------
# 【2026-11-21 修正】docs 頁面是舊譯，不得用來補缺口；此段停用，未認領的 pair 一律不補。
USE_DOCS_FILL = False
fill = []
pn = 0
if USE_DOCS_FILL:
    for i, p in enumerate(pairs):
        if p['q'] < 0 or p['used']:
            continue
        pn += 1
        tr = p['tr']
        fill.append({'n': 10 ** 6 + pn, 'key': 'P%04d' % pn, 'label': '鈔文',
                     'src': raw_slice_padded(p['q'], p['e']), 'trial': '', 'fin': '', 'rev': '',
                     'code': p['vol'], 'chunk': chunk_at(p['q']), 'origin': 'docs_pair',
                     'q': p['q'], 'e': p['e'], 'tr': tr, 'picksrc': 'docs', 'revised': False})
STAT['docs補單位'] = len(fill)
STAT['未認領pair'] = sum(1 for p in pairs if p['q'] >= 0 and not p['used'])

rows = units + fill
# ---------- 翻譯缺漏檢查 ----------
notr = [r['key'] for r in rows if not r['tr']]
STAT['無譯文單位'] = notr

# ---------- 重疊／缺口 ----------
iv = sorted((r['q'], r['e']) for r in rows if r['q'] >= 0)
cover = [0] * (len(H) + 1)
for a, b in iv:
    for i in range(a, min(b, len(H))):
        cover[i] += 1
overlap = sum(1 for c in cover[:len(H)] if c > 1)
runs = []
i = 0
while i < len(H):
    if cover[i] == 0:
        j = i
        while j < len(H) and cover[j] == 0:
            j += 1
        runs.append((i, j, j - i))
        i = j
    else:
        i += 1
STAT['覆蓋字數'] = sum(1 for c in cover[:len(H)] if c)
STAT['原文漢字'] = len(H)
STAT['重疊字數'] = overlap
STAT['缺口段數'] = len(runs)
STAT['缺口_ge20'] = [(a, b, n, H[a:b]) for a, b, n in runs if n >= 20]
STAT['缺口_lt20'] = [(a, b, n, H[a:b]) for a, b, n in runs if n < 20]

# ---------- 去重（同 raw 區間 + 同原文）----------
seen = set()
keep = []
dup = []
for r in sorted(rows, key=lambda x: (x['q'] if x['q'] >= 0 else 10 ** 9, x['n'])):
    k = (r['q'], r['e'], r['src'])
    if k in seen:
        dup.append((r['key'], r['q'], r['e']))
        continue
    seen.add(k)
    keep.append(r)
STAT['去重移除'] = dup

# ---------- 組成 jsonl ----------
out = []
for r in keep:
    ch = r['chunk'] or chunk_at(r['q'])
    vol = ch[:2] if ch.startswith('卷') else ''
    tr = r['tr']
    out.append({
        'book': '行事鈔', 'book_id': 'xingshichao', 'key': r['key'], 'label': r['label'],
        'source': r['src'],
        'translation': ('【%s】\n%s' % (r['label'], tr)) if tr else '',
        'revised': r['revised'],
        'segments': [{'label': r['label'], 'source': r['src'], 'translation': tr}],
        'raw_start': r['q'], 'raw_end': r['e'], 'vol': vol, 'chunk': ch,
        'origin': r['origin'], 'picksrc': r['picksrc'],
    })
STAT['輸出列數'] = len(out)
STAT['有位置'] = sum(1 for o in out if o['raw_start'] >= 0)
STAT['未定位'] = [o['key'] for o in out if o['raw_start'] < 0]
STAT['origin分布'] = {}
for o in out:
    STAT['origin分布'][o['origin']] = STAT['origin分布'].get(o['origin'], 0) + 1
STAT['chunk分布'] = {}
for o in out:
    STAT['chunk分布'][o['chunk']] = STAT['chunk分布'].get(o['chunk'], 0) + 1
STAT['vol分布'] = {}
for o in out:
    STAT['vol分布'][o['vol']] = STAT['vol分布'].get(o['vol'], 0) + 1
STAT['譯文總字數'] = sum(len(o['segments'][0]['translation']) for o in out)
STAT['原文總字數'] = sum(len(han(o['source'])) for o in out)
STAT['單位字數_最大'] = max(len(han(o['source'])) for o in out)
STAT['單位字數_中位'] = sorted(len(han(o['source'])) for o in out)[len(out) // 2]

# ---------- 寫檔 ----------
p = os.path.join(B, '定稿', 'xingshichao.jsonl')
bk = os.path.join(B, '定稿', '_舊_xingshichao.jsonl')
if not DRY:
    if not os.path.exists(bk):
        shutil.copy(p, bk)
    io.open(p, 'w', encoding='utf-8').writelines(
        json.dumps(o, ensure_ascii=False) + '\n' for o in out)
json.dump(STAT, io.open(os.path.join(B, '_src', '_xs_stat.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('=== 結果 ===')
for k in ('骨幹單位', '終審md', 'docs_pair', 'docs_pair_未定位', '無原文單位', '孤兒取回原文',
          '孤兒未取回', 'docs補單位', '未認領pair', '輸出列數', '有位置', '未定位', '覆蓋字數',
          '原文漢字', '重疊字數', '缺口段數', '無譯文單位', '譯文來源', 'origin分布', '譯文總字數'):
    print(k, '=', STAT[k])
print('缺口 >=20：%d 段 / %d 字（最大 %d）' % (
    len(STAT['缺口_ge20']), sum(x[2] for x in STAT['缺口_ge20']),
    max((x[2] for x in STAT['缺口_ge20']), default=0)))
print('缺口 <20 ：%d 段 / %d 字' % (
    len(STAT['缺口_lt20']), sum(x[2] for x in STAT['缺口_lt20'])))
print('骨幹未對齊pair邊界:', STAT['骨幹未對齊pair邊界'], STAT['骨幹未對齊樣本'])
print('重複移除:', len(dup))
