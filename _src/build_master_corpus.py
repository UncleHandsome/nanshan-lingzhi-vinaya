# -*- coding: utf-8 -*-
"""彙整五書定稿成單一順序總集，並產出總目錄。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = [
 ('xingshichao', '行事鈔', 'TXT/01_四分律刪繁補闕行事鈔.txt'),
 ('jieshu', '戒疏', 'TXT/02_四分律含注戒本疏.txt'),
 ('yeshu', '業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt'),
 ('nicao', '尼鈔', 'TXT/04_四分律比丘尼鈔.txt'),
 ('yichao', '義鈔', 'TXT/05_四分律拾毗尼義鈔.txt'),
]
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', str(s)))
def nonbody(t):
    t = t[:140]
    if t.startswith(('大覺慈父','九十單提法','百眾學法','四分戒本》者','甞聞毗尼藏','原夫大雄','疏卷第一')): return True
    if '【四分律' in t[:80] and '卷' in t[:100]: return True
    if '四分律含注戒本疏卷' in t[:50]: return True
    if t.startswith(('四分律刪補','四分律含注','四分律拾毗尼','四分律比丘尼鈔','南山三大部','底本')): return True
    if '篇第' in t[:80] and ('】' in t[:80] or '卷' in t[:60]): return True
    return False

allrows = []
stats = []
for order, (book, name, rawp) in enumerate(BOOKS, 1):
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''; mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c; mp.append(i)
    rows = [json.loads(x) for x in io.open(os.path.join(B, '定稿', book + '.jsonl'), encoding='utf-8') if x.strip()]
    rows.sort(key=lambda r: (r.get('raw_start', -1) < 0, r.get('raw_start', 0), r.get('raw_end', 0), r['key']))
    located = exact = 0
    iv = []
    for r in rows:
        a, b = r.get('raw_start', -1), r.get('raw_end', -1)
        if a >= 0 and b > a:
            located += 1
            iv.append((a, b))
            if han(r.get('source', '')) == h[a:b]:
                exact += 1
        allrows.append({'book_order': order, 'book': name, 'book_id': book, 'key': r['key'],
                        'label': r.get('label', ''), 'source': r.get('source', ''),
                        'translation': r.get('translation', ''), 'raw_start': a, 'raw_end': b,
                        'vol': r.get('vol', ''), 'chunk': r.get('chunk', '')})
    cover = [0] * len(h)
    for a, b in iv:
        for i in range(a, min(b, len(h))):
            cover[i] += 1
    body = other = 0
    i = 0
    while i < len(h):
        if cover[i] == 0:
            j = i
            while j < len(h) and cover[j] == 0:
                j += 1
            if j - i >= 20:
                if nonbody(raw[mp[i]:mp[i]+140]): other += 1
                else: body += 1
            i = j
        else:
            i += 1
    overlap = sum(1 for a, b in iv if any(cover[i] > 1 for i in range(a, min(b, len(h)))))
    stats.append((name, len(rows), located, exact, body, other, overlap, min(iv)[0] if iv else -1, max(iv)[1] if iv else -1))

io.open(os.path.join(B, '定稿', '五書_總集.jsonl'), 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in allrows)

L = ['# 五書總彙整（從頭順序）', '',
     '> 2026-11-21。以 `定稿/*.jsonl` 為唯一來源，按書序、raw 順序彙整。', '',
     '## 總表', '',
     '| 書 | 單位 | 有位置 | source==raw | 正文缺口 | 非正文 | 重疊 | raw 範圍 |',
     '|:--|--:|--:|--:|--:|--:|--:|:--|']
for name, n, loc, exact, body, other, ov, a, b in stats:
    L.append('| %s | %d | %d | %d | %d | %d | %d | %d–%d |' % (name, n, loc, exact, body, other, ov, a, b))
L += ['', '## 檔案', '',
      '```text',
      '定稿/五書_總集.jsonl       全部單位，依書序／raw 排序',
      '定稿/xingshichao.jsonl',
      '定稿/jieshu.jsonl',
      '定稿/yeshu.jsonl',
      '定稿/nicao.jsonl',
      '定稿/yichao.jsonl',
      '```', '',
      '## 目前判定', '',
      '- 行事鈔：正文缺口 0、重疊 0。',
      '- 尼鈔：正文缺口 0、重疊 0。',
      '- 義鈔：正文缺口 0、重疊 0。',
      '- 業疏：正文缺口 3、重疊 0；待重驗。',
      '- 戒疏：正文缺口 20、重疊 0；但 4,462 筆 source ≠ raw，**尚未完成對齊**。',
      '', '## 未完成', '',
      '```text',
      '戒疏：source 抓取不乾淨，須從 _終審 區塊重抓，不能沿用現有缺口。',
      '業疏：3 個正文缺口待補。',
      '```', '']
io.open(os.path.join(B, '重作材料_長段', '五書_總彙整.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('rows', len(allrows))
for s in stats: print(s)
