# -*- coding: utf-8 -*-
"""產出業疏偏移區段的重譯材料（每 chunk 一份）"""
import glob, os, io, re, collections, json
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, '會本材料_11-30', '業疏重譯')
os.makedirs(OUT, exist_ok=True)
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

# chunk 原文
chunks = {}
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '03_業疏', '*.txt'))):
    key = os.path.basename(f)[:-4]
    chunks[key] = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]

# 建立定位索引
index = []
for key, sp in chunks.items():
    for i, s in enumerate(sp):
        h = han(s)
        if len(h) >= 8:
            index.append((key, i, h[:24]))

def locate(src):
    h = han(src)
    if len(h) < 8:
        return None
    for key, i, n in index:
        if n == h[:24]:
            return key, i
    for key, i, n in index:
        if n[:12] == h[:12]:
            return key, i
    return None

agg = collections.defaultdict(set)
for f in sorted(glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
    d = Document(f)
    seen = set()
    last = ''
    for p in d.paragraphs:
        t = p.text.strip()
        if t.startswith('【疏】') or t.startswith('【記】'):
            last = t[3:].strip()
            continue
        if len(t) < 30:
            continue
        if t in seen:
            loc = locate(last)
            if loc:
                agg[loc[0]].add(loc[1])
        else:
            seen.add(t)

n = 0
for key, idxs in sorted(agg.items()):
    sp = chunks.get(key, [])
    lo, hi = min(idxs), max(idxs)
    body = '\n'.join('%d. %s' % (i + 1, sp[i]) for i in range(lo, min(hi + 1, len(sp))))
    txt = """# 業疏重譯：%s（第 %d–%d 段）

以下段落是《四分律刪補隨機羯磨疏》原文，請逐段翻成現代白話。

規則：
1. 一段一段對應，編號不可改。
2. 只回 JSON：{"%s": {"%d": "白話…", "%d": "白話…"}}

## 原文
%s
""" % (key, lo + 1, min(hi + 1, len(sp)), key, lo + 1, lo + 2, body)
    io.open(os.path.join(OUT, '%s_%03d-%03d.md' % (key, lo + 1, min(hi + 1, len(sp)))), 'w', encoding='utf-8').write(txt)
    n += 1
print('產出', n, '份重譯材料 →', OUT)
