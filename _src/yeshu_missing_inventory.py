# -*- coding: utf-8 -*-
"""盤點業疏各 chunk：原文段數 vs 白話段數，列出缺譯範圍"""
import glob, os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
rows = []
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '03_業疏', '*.txt'))):
    key = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '03_業疏', key + '.txt')
    tt = []
    if os.path.exists(tp):
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    rows.append((key, len(sp), len(tt)))

miss = [(k, a, b) for k, a, b in rows if b < a]
print('| chunk | 原段 | 譯段 | 缺 |')
print('|:--|--:|--:|--:|')
for k, a, b in miss:
    print('| %s | %d | %d | %d |' % (k, a, b, a - b))
print('總缺', sum(a - b for k, a, b in miss), '段，涉及', len(miss), 'chunk')
json.dump(miss, io.open(os.path.join(B, 'AI語譯', '_work', 'yeshu_missing.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
