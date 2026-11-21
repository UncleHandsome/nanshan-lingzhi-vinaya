# -*- coding: utf-8 -*-
"""尼鈔：重建 定稿/nicao.jsonl（小單位 + 頁面小 pair 補缺口）。

流程
1. `_終審/*.md` 逐檔抽 `■ …（原文）` 之後正文，截斷於【待審譯文】/【裁決】/【後文背景】/下一 ■。
2. 譯文序：`_定稿/<key>.txt` > `_終修/回覆/<key>_回.txt` > `_終審【待審譯文】`。
3. 4 個缺 md 的 key（39/432/464/556）：由 `_終審/回覆/<key>_回.txt` 逐句「原文」引文重建，並與 raw 缺口逐字驗證。
4. 定位用單調游標：按 key 順序，從上一單位結尾往後找；找不到才回頭全域找並記錄。
5. 剩餘缺口若能在 docs/nicao 找到同一段的小 pair，就用該 pair 譯文補（不合併 HTML、不改 HTML）。
6. 只做「同 raw 區間＋同原文」去重。
"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '尼鈔')
OUT = os.path.join(B, '定稿', 'nicao.jsonl.new')

raw = io.open(os.path.join(B, 'TXT', '04_四分律比丘尼鈔.txt'), encoding='utf-8').read()
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def source_block(md):
    m = re.search(r'■\s*([^\n（]*?)（原文）', md)
    if not m:
        return '', ''
    s = md[m.end():].strip()
    cut = re.search(r'\n■\s*[^\n（]*（|【待審譯文】|【裁決|【後文背景】|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return m.group(1).strip(), s


def trans_block(md):
    j = md.rfind('【待審譯文】')
    if j < 0:
        return ''
    s = md[j + len('【待審譯文】'):].strip()
    cut = re.search(r'【後文背景|【裁決|\n■|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return s


def clean(tr):
    lines = [x for x in tr.strip().splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    return '\n'.join(lines).strip()


def strip_label(t):
    t = t.strip()
    m = re.match(r'^【([^】]+)】\s*', t)
    return t[m.end():].strip() if m else t


def trim_hr(t):
    """去掉譯文裡誤留的 Markdown 分隔線（如 674.txt 結尾的 ---）。"""
    lines = t.strip().splitlines()
    while lines and re.match(r'^\s*-{3,}\s*$', lines[-1]):
        lines.pop()
    while lines and re.match(r'^\s*-{3,}\s*$', lines[0]):
        lines.pop(0)
    return '\n'.join(lines).strip()


VOL = {'00': ('卷上', '卷上之上'), '01': ('卷上', '卷上之上'), '02': ('卷上', '卷上之下'),
       '03': ('卷中', '卷中之上'), '04': ('卷中', '卷中之下'), '05': ('卷下', '卷下之上'),
       '06': ('卷下', '卷下之下')}


def meta(md):
    m = re.search(r'（出處：([0-9]{2})([ab]?)_([^，]*)', md)
    return VOL[m.group(1)] if m else ('', '')


td = os.path.join(ROOT, '_終審')
rev = os.path.join(ROOT, '_終修', '回覆')
fin = os.path.join(ROOT, '_定稿')

# ---------- 1/2. md 單位 ----------
keys = sorted([f[:-3] for f in os.listdir(td) if f.endswith('.md')], key=int)
rows = []
kind_count = {'定稿': 0, '終修': 0, '終審': 0}
for key in keys:
    md = io.open(os.path.join(td, key + '.md'), encoding='utf-8').read()
    label, src = source_block(md)
    if not label:
        label = '鈔文'
    fp = os.path.join(fin, key + '.txt')
    rp = os.path.join(rev, key + '_回.txt')
    if os.path.exists(fp):
        tr = trim_hr(io.open(fp, encoding='utf-8').read())
        kind = '定稿'
    elif os.path.exists(rp):
        tr = trim_hr(io.open(rp, encoding='utf-8').read())
        kind = '終修'
    else:
        tr = clean(trans_block(md))
        kind = '終審'
    kind_count[kind] += 1
    vol, chunk = meta(md)
    rows.append({'book': '尼鈔', 'book_id': 'nicao', 'key': key, 'label': label,
                 'source': src, 'translation': tr, 'revised': os.path.exists(rp),
                 '_kind': kind, '_chunk_id': '', 'segments': [],
                 'raw_start': -1, 'raw_end': -1, 'vol': vol, 'chunk': chunk})
print('md units', len(rows), kind_count)

# ---------- 3. 4 個缺 md 的 key ----------
QUOTE_PAT = {
    '39': re.compile(r'原文「([^」]+)」'),
    '432': re.compile(r'^\d+\.\s*\*\*「([^」]+)」\*\*\s*→'),
    '464': re.compile(r'\*\*原文\*\*：「([^」]+)」'),
    '556': re.compile(r'^\d+\.\s*\*\*原文「([^」]+)」'),
}
missing_rows = {}
for key, pat in QUOTE_PAT.items():
    t = io.open(os.path.join(td, '回覆', key + '_回.txt'), encoding='utf-8').read()
    qs = []
    for line in t.splitlines():
        m = pat.search(line.strip())
        if m:
            qs.append(m.group(1))
    joined = ''.join(han(x) for x in qs)
    joined = joined.replace('鈔文原文', '', 1) if joined.startswith('鈔文原文') else joined
    missing_rows[key] = joined
    print('recover', key, 'quotes', len(qs), 'len', len(joined))

# ---------- 4. 單調定位 ----------
rows.sort(key=lambda r: int(r['key']))
for key, joined in missing_rows.items():
    rp = os.path.join(rev, key + '_回.txt')
    fp = os.path.join(fin, key + '.txt')
    tr = trim_hr(io.open(fp, encoding='utf-8').read()) if os.path.exists(fp) else ''
    rows.append({'book': '尼鈔', 'book_id': 'nicao', 'key': key, 'label': '鈔文',
                 'source': '', 'translation': tr, 'revised': os.path.exists(rp),
                 '_kind': '定稿', '_recover': joined, '_chunk_id': '', 'segments': [],
                 'raw_start': -1, 'raw_end': -1, 'vol': '', 'chunk': ''})
rows.sort(key=lambda r: int(r['key']))

cursor = 0
back = []
for r in rows:
    if not r['source']:
        continue
    s = han(r['source'])
    q = h.find(s, cursor)
    if q < 0:
        q = h.find(s)
        back.append((r['key'], q, cursor))
    if q >= 0:
        r['raw_start'] = q
        r['raw_end'] = q + len(s)
        cursor = max(cursor, q + len(s))
print('backtrack', len(back), back[:10])

cover = [0] * len(h)
for r in rows:
    if r['raw_start'] >= 0:
        for i in range(r['raw_start'], min(r['raw_end'], len(h))):
            cover[i] += 1
gaps = []
i = 0
while i < len(h):
    if cover[i] == 0:
        j = i
        while j < len(h) and cover[j] == 0:
            j += 1
        gaps.append((i, j))
        i = j
    else:
        i += 1
print('gaps before recover', len(gaps))

# 4 個缺 md key 對到缺口
for r in rows:
    if r['source'] or '_recover' not in r:
        continue
    joined = r['_recover']
    hit = None
    for a, b in gaps:
        if h[a:b] == joined:
            hit = (a, b)
            break
    print('  recover', r['key'], 'hit', hit)
    if hit:
        a, b = hit
        r['source'] = joined
        r['raw_start'] = a
        r['raw_end'] = b
# 重算覆蓋
cover = [0] * len(h)
for r in rows:
    if r['raw_start'] >= 0:
        for i in range(r['raw_start'], min(r['raw_end'], len(h))):
            cover[i] += 1
gaps = []
i = 0
while i < len(h):
    if cover[i] == 0:
        j = i
        while j < len(h) and cover[j] == 0:
            j += 1
        gaps.append((i, j))
        i = j
    else:
        i += 1
print('gaps after recover', len(gaps), sum(b - a for a, b in gaps))

# ---------- 5. 頁面 pair 補缺口 ----------
pages = json.loads(io.open(os.path.join(B, '_src', '_nicao_pages.json'), encoding='utf-8').read())
pload = []
for i, p in enumerate(pages):
    s = han(re.sub(r'^【[^】]*】', '', p['o']))
    pload.append((i, s, p['t']))

def clean_page_tr(t):
    """頁面譯文清掉曾被誤植進 HTML 的 Markdown 報告／標題。"""
    t = t.strip()
    for pat in ('\n\n# ', '\n\n| ', '\n###', '尼鈔_缺口', '【裁決', '【待審譯文】'):
        k = t.find(pat)
        if k >= 0:
            t = t[:k]
    return t.strip()


# 4 個大缺口：pair 原文＝缺口＋尾字，譯文只覆蓋缺口；16252 這一條要切掉尾段白文
BIG = {2561: dict(pair=234, cut=None),
       11884: dict(pair=78, cut=None),
       16252: dict(pair=116, cut='然後稟白說：'),
       70476: dict(pair=651, cut=None)}
added = []
for a, b in gaps:
    txt = h[a:b]
    if a in BIG:
        pi = BIG[a]['pair']
        tr = clean_page_tr(strip_label(pload[pi][2]))
        if BIG[a]['cut']:
            k = tr.find(BIG[a]['cut'])
            print('  cut', a, 'mark at', k, 'of', len(tr))
            tr = tr[:k + len(BIG[a]['cut'])]
        added.append((a, b, txt, pi, 'big', tr))
        continue
    sel = [x for x in pload if x[1] == txt]
    mode = 'exact'
    if not sel:
        # pair 原文 = 缺口 + 篇題尾字；譯文只到缺口結尾
        cand = [x for x in pload if x[1].startswith(txt)
                and len(x[1]) - len(txt) <= 20 and '篇第' in x[1][len(txt):]]
        if cand:
            sel = sorted(cand, key=lambda x: len(x[1]) - len(txt))[:1]
            mode = 'gap+篇題'
    if not sel:
        # 缺口 = pair 原文 + 極少字（如「（第）五出眾」，pair 少了開頭一字）
        cand = [x for x in pload if x[1] in txt and len(txt) - len(x[1]) <= 5 and txt.startswith('第')]
        if cand:
            sel = sorted(cand, key=lambda x: len(txt) - len(x[1]))[:1]
            mode = 'pair-short'
    if not sel:
        print('  NO PAIR', a, b, b - a, repr(txt[:40]))
        continue
    pi, ps, pt = sel[0]
    added.append((a, b, txt, pi, mode, clean_page_tr(strip_label(pt))))
print('gap fill from pages', len(added))

# ---------- 6. 去重（只同區間＋同原文） ----------
seen = set()
keep = []
removed = 0
for r in rows:
    k = (r['raw_start'], r['raw_end'], r['source'])
    if r['raw_start'] >= 0 and k in seen:
        removed += 1
        continue
    seen.add(k)
    keep.append(r)
rows = keep
print('dedupe removed', removed)

# ---------- 7. 補缺口 rows 併入 ----------
for n, (a, b, txt, pi, mode, tr) in enumerate(added, 1):
    rows.append({'book': '尼鈔', 'book_id': 'nicao', 'key': 'GAP%02d' % n, 'label': '鈔文',
                 'source': txt, 'translation': '【鈔文】\n' + tr, 'revised': False,
                 '_kind': '頁面', '_chunk_id': '', 'segments': [],
                 'raw_start': a, 'raw_end': b, 'vol': '', 'chunk': ''})

# ---------- 8. segments / vol / chunk / 排序 ----------
rows.sort(key=lambda r: (r['raw_start'] if r['raw_start'] >= 0 else 10 ** 9, r['key']))
for i, r in enumerate(rows):
    if not r['vol']:
        for j in range(i - 1, -1, -1):
            if rows[j]['vol']:
                r['vol'], r['chunk'] = rows[j]['vol'], rows[j]['chunk']
                break
    r['segments'] = [{'label': r['label'], 'source': r['source'],
                      'translation': strip_label(r['translation'])}]
    r.pop('_kind', None)
    r.pop('_chunk_id', None)
    r.pop('_recover', None)

io.open(OUT, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('wrote', OUT, 'rows', len(rows))
