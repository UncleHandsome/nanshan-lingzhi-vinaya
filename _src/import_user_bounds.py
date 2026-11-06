# -*- coding: utf-8 -*-
"""修復使用者提供的 bounds.json / splits，轉成 _work 標準檔"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '會本材料_11-30')
BD = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')
SD = os.path.join(B, 'AI語譯', '_work', 'pian_splits')
os.makedirs(BD, exist_ok=True)
os.makedirs(SD, exist_ok=True)

# ---- bounds.json ----
txt = io.open(os.path.join(SRC, 'bounds.json'), encoding='utf-8-sig').read()
parts = re.split(r'"篇(\d+)_bounds"', txt)
out = {}
for i in range(1, len(parts) - 1, 2):
    p = int(parts[i])
    body = parts[i + 1]
    pairs = []
    for blk in re.findall(r'\{[^{}]*\}', body):
        nums = [int(x) for x in re.findall(r'\d+', blk)]
        if len(nums) >= 2:
            c, n = nums[0], nums[1]
            if 1 <= c <= 500 and 1 <= n <= 5000:
                pairs.append((c, n))
    # 去重、c 遞增
    seen = {}
    for c, n in pairs:
        seen[c] = n
    bs = [{'c': c, 'n': seen[c]} for c in sorted(seen)]
    out[p] = bs
    cn = [c for c, n in pairs]
    print('篇%d：%d 筆，c %d..%d' % (p, len(bs), min(cn), max(cn)))
    json.dump({'bounds': bs}, io.open(os.path.join(BD, 'bounds_篇%02d.json' % p), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

# ---- splits_14 ----
d = json.load(io.open(os.path.join(SRC, 'splits_14.json'), encoding='utf-8-sig'))
sp = d.get('splits', d if isinstance(d, list) else [])
json.dump({'splits': sp}, io.open(os.path.join(SD, 'split_篇14.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('篇14 splits', len(sp))

# ---- splits_18-30 ----
d2 = json.load(io.open(os.path.join(SRC, 'splits_18-30.json'), encoding='utf-8-sig'))
sp2 = d2.get('splits', [])
by = {}
for e in sp2:
    ch = str(e.pop('chapter', '')).strip()
    m = re.search(r'(\d+)', ch)
    if not m:
        continue
    by.setdefault(int(m.group(1)), []).append(e)
for p, arr in sorted(by.items()):
    json.dump({'splits': arr}, io.open(os.path.join(SD, 'split_篇%02d.json' % p), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('篇%d splits %d' % (p, len(arr)))
