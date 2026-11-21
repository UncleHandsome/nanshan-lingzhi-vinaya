# -*- coding: utf-8 -*-
"""義鈔重建：從 _終審/_終修 的 ■ 鈔文（原文）區塊取原文。"""
import io, json, os, re, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '義鈔')
LT = os.path.join(ROOT, '_長段')
raw = io.open(os.path.join(B, 'TXT', '05_四分律拾毗尼義鈔.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def source_block(md):
    m = re.search(r'■\s*[^\n（]*（原文）', md)
    if not m:
        return ''
    s = md[m.end():].strip()
    cut = re.search(r'\n■\s*[^\n（]*（|【裁決|【後文背景】|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return s

def translation(md):
    j = md.rfind('【待審譯文】')
    if j < 0:
        return ''
    s = md[j + 6:].strip()
    cut = re.search(r'【後文背景】|【裁決|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return s

def clean(tr):
    lines = [x for x in tr.strip().splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    return '\n'.join(lines).strip()

rows = []
for td, fd, rev, prefix in ((os.path.join(ROOT, '_終審'), os.path.join(ROOT, '_定稿'), os.path.join(ROOT, '_終修', '回覆'), ''),
                            (os.path.join(LT, '_終審'), os.path.join(LT, '_定稿'), '', 'L:')):
    for f in sorted(os.listdir(td)):
        if not f.endswith('.md'):
            continue
        key = f[:-3]
        md = io.open(os.path.join(td, f), encoding='utf-8').read()
        src = source_block(md)
        if not src:
            continue
        tr = translation(md)
        rp = os.path.join(rev, key + '_回.txt') if rev else ''
        if rp and os.path.exists(rp):
            tr = io.open(rp, encoding='utf-8').read()
        elif os.path.exists(os.path.join(fd, key + '.txt')):
            tr = io.open(os.path.join(fd, key + '.txt'), encoding='utf-8').read()
        tr = clean(tr)
        if not tr:
            continue
        s = han(src)
        q = h.find(s[:20])
        if q < 0:
            q = h.find(s[:12])
        rows.append({'book': '義鈔', 'book_id': 'yichao', 'key': prefix + key, 'label': '鈔文',
                     'source': src, 'translation': tr, 'revised': bool(rp and os.path.exists(rp)),
                     'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                     'raw_start': q, 'raw_end': q + len(s) if q >= 0 else -1, 'vol': '', 'chunk': ''})
p = os.path.join(B, '定稿', 'yichao.jsonl')
if os.path.exists(p):
    shutil.copy(p, os.path.join(B, '定稿', '_舊_yichao.jsonl'))
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows), 'located', sum(1 for r in rows if r['raw_start'] >= 0), 'long', sum(1 for r in rows if r['key'].startswith('L:')))
