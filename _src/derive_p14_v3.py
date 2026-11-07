import io, os, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
# 還原使用者 319 界
import subprocess, sys
subprocess.run([sys.executable, os.path.join(B, '_src', 'merge_p14.py')], check=False)

bs = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇14.json'), encoding='utf-8-sig'))['bounds']
bs = [(int(x['c']), int(x['n'])) for x in bs]
cmap = {}
for i, (c, n) in enumerate(bs):
    end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
    for k in range(n, max(n, end) + 1):
        cmap[k] = c
N = max(cmap) if cmap else 0

sp = {int(e['n']): e for e in json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), encoding='utf-8-sig'))['splits']}
out = []
for n, e in sorted(sp.items()):
    c = cmap.get(n)
    if c is None:
        continue
    # 下一個不同鈔號
    nc = None
    for k in range(n + 1, n + 20):
        if cmap.get(k, c) > c:
            nc = cmap[k]
            break
    if nc is None:
        continue
    k = nc - c + 1
    if len(e['markers']) != k - 1:
        continue
    out.append({'n': n, 'base': c, 'markers': e['markers'], 'targets': list(range(c, nc + 1))})

json.dump({'splits': out}, io.open(os.path.join(B, 'AI語譯', '_work', 'pian_split_out', 'split_篇14.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('accepted splits', len(out))
