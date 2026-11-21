# -*- coding: utf-8 -*-
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '重作材料_長段', 'output (4).txt')
BOOKS = {
 '尼鈔': ('nicao', '尼鈔', 'TXT/04_四分律比丘尼鈔.txt'),
 '業疏': ('yeshu', '業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt'),
 '戒疏': ('jieshu', '戒疏', 'TXT/02_四分律含注戒本疏.txt'),
}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
text = io.open(SRC, encoding='utf-8').read()
for name, (book, label, rawp) in BOOKS.items():
    raw = io.open(os.path.join(B, rawp), encoding='utf-8').read()
    h = ''
    mp = []
    for i, c in enumerate(raw):
        if '\u4e00' <= c <= '\u9fff':
            h += c
            mp.append(i)
    p = os.path.join(B, '定稿', book + '.jsonl')
    rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
    rows = [r for r in rows if not r['key'].startswith(('GAP', 'FIX-'))]
    cover = [0] * len(h)
    for r in rows:
        a, b = r.get('raw_start', -1), r.get('raw_end', -1)
        if a >= 0 and b > a:
            for i in range(a, min(b, len(h))):
                cover[i] += 1
    pat = re.compile(r'^## %s-G(\d+)\s*\n(.*?)(?=^## %s-G|\Z)' % (name, name), re.M | re.S)
    added = 0
    for m in pat.finditer(text):
        g = int(m.group(1))
        blocks = [x.strip() for x in re.split(r'\n\s*\n', m.group(2)) if x.strip()]
        srcs, trs = [], []
        for b in blocks:
            clean = re.sub(r'^(?:【[^】]+】\s*)+', '', b).strip()
            clean = re.sub(r'^【[^】]+】', '', clean).strip()
            th = han(clean)
            if not th:
                continue
            if h.find(th[:20]) >= 0 or h.find(th[:12]) >= 0:
                srcs.append(clean)
            else:
                trs.append(clean)
        if not srcs or not trs:
            continue
        src = '\n'.join(srcs)
        tr = '\n'.join(trs)
        sh = han(src)
        q = h.find(sh[:20])
        if q < 0:
            q = h.find(sh[:12])
        if q < 0:
            continue
        e = q + len(sh)
        if all(cover[i] for i in range(q, min(e, len(h)))):
            continue
        if any(cover[i] for i in range(q, min(e, len(h)))):
            continue
        rows.append({'book': label, 'book_id': book, 'key': '%s-G%02d' % (name, g), 'label': '疏文',
                     'source': src, 'translation': tr, 'revised': True,
                     'segments': [{'label': '疏文', 'source': src, 'translation': tr}],
                     'raw_start': q, 'raw_end': e, 'vol': '', 'chunk': ''})
        for i in range(q, min(e, len(h))):
            cover[i] += 1
        added += 1
    io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
    print(name, 'added', added, 'rows', len(rows))
