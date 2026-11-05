
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ju_path = os.path.join(D, '04_四分律比丘尼鈔_句讀.txt')
src_path = os.path.join(D, 'TXT', '04_四分律比丘尼鈔.txt')
sup_path = os.path.join(D, 'TXT_句讀', '_缺段', '補.txt')
BT = chr(96) * 3

def han(s): return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')

ju = io.open(ju_path, encoding='utf-8').read()
src = han(io.open(src_path, encoding='utf-8').read())
juh = han(ju)

sup = io.open(sup_path, encoding='utf-8').read()
pat = re.compile(BT + r'(?:text)?\r?\n([\s\S]*?)' + BT)
blocks = pat.findall(sup)
nb = blocks[1]
parts = re.split(r'【缺段(\d)】', nb)
segs = {}
for i in range(1, len(parts), 2):
    segs[int(parts[i])] = parts[i+1].strip()
print('patch chars', {k: len(v) for k, v in segs.items()})

gaps = [(9684, 9720, 4), (46836, 46884, 3), (72372, 72516, 1), (72528, 72564, 2)]
for a, b, idx in sorted(gaps, reverse=True):
    pre = src[max(0, a-14):a]
    pos = juh.rfind(pre)
    if pos < 0:
        print('anchor miss', idx); continue
    cnt = pos + len(pre)
    rawpos = len(ju); c = 0
    for i, ch in enumerate(ju):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            c += 1
            if c == cnt:
                rawpos = i + 1; break
    ju = ju[:rawpos] + segs[idx] + ju[rawpos:]
    juh = han(ju)
    print('inserted seg', idx, 'raw', rawpos)
io.open(os.path.join(D, '04_四分律比丘尼鈔_句讀_v2.txt'), 'w', encoding='utf-8').write(ju)
print('saved v2 chars', len(ju))
