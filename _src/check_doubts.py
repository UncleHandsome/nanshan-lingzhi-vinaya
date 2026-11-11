# -*- coding: utf-8 -*-
"""檢查存疑材料與裁判結果的覆蓋率。"""
import io, os, re, glob, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\存疑材料\complex_存疑'


def norm(x):
    x = re.sub(r'（[^）]*）', '', x)
    x = re.sub(r'-[A-Z]$', '', x)
    return x.strip()


mat = []
for f in sorted(glob.glob(os.path.join(B, 'complex_*.md'))):
    t = io.open(f, encoding='utf-8').read()
    mat += [norm(i) for i in re.findall(r'【存疑\s*([^】]+)】', t)]

jud, verd = [], []
for f in ('return.txt', 're2.txt', 're3.txt'):
    t = io.open(os.path.join(B, f), encoding='utf-8', errors='ignore').read()
    found = re.findall(r'(?m)^#{2,4}\s*([^\s｜|]*?)\s*｜\s*(是錯|不是錯|材料不足)', t)
    jud += [norm(a) for a, _ in found]
    verd += [b for _, b in found]

ms, js = set(mat), set(jud)
print('材料條目', len(mat), '去重', len(ms))
print('判定條目', len(jud), '去重', len(js))
print('判定分佈', dict(collections.Counter(verd)))
print('未判定（材料有、判定無）', sorted(ms - js))
print('判定有材料無', sorted(js - ms)[:15])
