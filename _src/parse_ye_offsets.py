# -*- coding: utf-8 -*-
"""解析 ye_new.txt 的各分塊位移量 → ys_offsets.json"""
import io, re, json, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
t = io.open(os.path.join(B, '業疏材料', 'ye_new.txt'), encoding='utf-8').read()

# 形如 `07a_卷二之一`（位移 +29）
pat = re.compile(r'`?(\d{2}[ab])_([^`\n（(]{1,12})`?\s*[（(]\s*位移\s*([+-]?\s*\d+)')
offs = {}
for m in pat.finditer(t):
    key = m.group(1)
    v = int(m.group(3).replace(' ', ''))
    offs.setdefault(key, v)
# 形如【本表原文第 N 行】＝【白話第 N+34 行】 也可能是其他寫法
if not offs:
    for m in re.finditer(r'(\d{2}[ab])[^\n]{0,30}?位移\s*([+-]?\d+)', t):
        offs.setdefault(m.group(1), int(m.group(2)))
json.dump(offs, io.open(os.path.join(B, 'AI語譯', '_work', 'ys_offsets.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('分塊', len(offs))
for k in sorted(offs):
    print('  %-5s %+d' % (k, offs[k]))
