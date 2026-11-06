# -*- coding: utf-8 -*-
"""修正重複尾巴、篇3 鈔18 起後移、篇5 鈔21-23 對位、移除篇2 記35 切點"""
import io, os, json, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) builder：補前篇尾巴前先檢查是否已存在
p = os.path.join(B, '_src', 'mk_pian_split.py')
s = io.open(p, encoding='utf-8').read()
old = """        d = Document(fp)
        emit_ji_to(d, '【記%03d】（續前篇）' % len(ZI[p - 2]), head, htr)"""
new = """        d = Document(fp)
        probe = ''.join(head.split())[:16]
        exist = any(probe and probe in ''.join(x.text.split()) for x in d.paragraphs)
        if exist:
            continue
        emit_ji_to(d, '【記%03d】（續前篇）' % len(ZI[p - 2]), head, htr)"""
assert old in s
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('append guard added')

# 2) 篇3 bounds c18-c21 各 +1
fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇03.json')
d = json.load(io.open(fp, encoding='utf-8-sig'))
for x in d['bounds']:
    if x['c'] in (18, 19, 20, 21):
        x['n'] += 1
json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇3 c18-21 +1')

# 3) 篇5：bounds c22=55、c23=56；記54 切「第七。人非中」
fp5 = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇05.json')
d5 = json.load(io.open(fp5, encoding='utf-8-sig'))
for x in d5['bounds']:
    if x['c'] == 22:
        x['n'] = 55
    elif x['c'] == 23:
        x['n'] = 56
json.dump(d5, io.open(fp5, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
mp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇05.json')
m = json.load(io.open(mp, encoding='utf-8-sig'))
m['splits'] = [e for e in m['splits'] if int(e['n']) != 54]
m['splits'].append({"n": 54, "base": 20, "markers": ["第七。人非中"], "targets": [20, 21]})
json.dump(m, io.open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇5 c22/23 + 記54 split')

# 4) 篇2 移除記35 切點（整段歸鈔10）
mp2 = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇02.json')
m2 = json.load(io.open(mp2, encoding='utf-8-sig'))
m2['splits'] = [e for e in m2['splits'] if int(e['n']) != 35]
json.dump(m2, io.open(mp2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇2 記35 split removed')
