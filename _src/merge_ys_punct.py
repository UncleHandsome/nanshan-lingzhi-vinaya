# -*- coding: utf-8 -*-
"""把 AI 補的句讀併入 yeshu_punct.json（逐段驗證漢字序列一致）"""
import io, os, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
P = os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json')
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(B, 'AI語譯', '_work', 'ys_punct_out.json')

han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
segs = json.load(io.open(P, encoding='utf-8'))
d = json.load(io.open(src, encoding='utf-8'))
blocks = d.get('blocks') or d.get('result') or []

# 分塊 offset
offsets = {}
gi = 0
for f in sorted(os.listdir(S), key=lambda x: (0 if x.startswith('00_') else 1, x)):
    if not f.endswith('.txt'):
        continue
    k = f[:-4]
    n = len([x for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()])
    offsets[k] = gi
    gi += n

fixed = 0
for blk in blocks:
    k = blk['key']
    texts = blk['texts']
    if k not in offsets:
        print('未知分塊', k)
        continue
    base = offsets[k]
    for i, txt in enumerate(texts):
        j = base + i
        if j >= len(segs):
            break
        if han(txt) == han(segs[j]):
            segs[j] = txt.strip()
            fixed += 1
        else:
            print('  字序不符', k, i)
print('併入', fixed, '段')
json.dump(segs, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False)
tot = sum(1 for x in segs if re.search(r'[，。、；：？！]', x))
print('總段', len(segs), '有標點', tot, '%.1f%%' % (100.0 * tot / len(segs)))
