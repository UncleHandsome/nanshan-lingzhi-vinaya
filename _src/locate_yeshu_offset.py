# -*- coding: utf-8 -*-
"""定位業疏對照本中「白話重複」所對應的原文 chunk，產出需重譯清單"""
import glob, os, io, re, json, collections
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

# 建立 chunk 索引
index = []   # (key, idx, norm20)
chunks = {}
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '03_業疏', '*.txt'))):
    key = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    chunks[key] = sp
    for i, s in enumerate(sp):
        h = han(s)
        if len(h) >= 8:
            index.append((key, i, h[:24]))

def locate(src):
    h = han(src)
    if len(h) < 8:
        return None
    probe = h[:24]
    for key, i, n in index:
        if n == probe:
            return key, i
    # 放寬：前 12 字
    probe = h[:12]
    for key, i, n in index:
        if n[:12] == probe:
            return key, i
    return None

rows = []
for f in sorted(glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs]
    seen = set()
    last_src = ''
    hits = collections.Counter()
    ranges = collections.defaultdict(list)
    for t in ps:
        if t.startswith('【疏】') or t.startswith('【記】'):
            last_src = t[3:].strip()
            continue
        if len(t) < 30:
            continue
        if t in seen:
            loc = locate(last_src)
            if loc:
                hits[loc[0]] += 1
                ranges[loc[0]].append(loc[1])
        else:
            seen.add(t)
    vol = re.search(r'卷(.)', os.path.basename(f)).group(1)
    for key, cnt in hits.most_common():
        rows.append((vol, key, cnt, min(ranges[key]), max(ranges[key]), len(chunks.get(key, []))))

rows.sort(key=lambda r: (r[0], r[1]))
lines = ['# 業疏偏移 chunk 清單（白話重複集中處）', '',
         '| 卷 | chunk | 重複筆數 | 疏段索引範圍 | 該 chunk 段數 |',
         '|:--:|:--|--:|:--|--:|']
for vol, key, cnt, lo, hi, total in rows:
    lines.append('| %s | %s | %d | %d–%d | %d |' % (vol, key, cnt, lo, hi, total))
lines.append('')
lines.append('說明：重複筆數＝該 chunk 內被錯誤共用同一段白話的疏/記段落數；索引範圍為這些段落在該 chunk 的位置。')
io.open(os.path.join(B, '業疏偏移chunk清單.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
