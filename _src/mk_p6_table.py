# -*- coding: utf-8 -*-
"""輸出篇6 的鈔↔記對照清單（供人工檢視）"""
import io, os, re, json, sys, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
idx = 5
sec = SECS[idx]; zi = ZI[idx]; am = AM[str(idx)]
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')

chao = [it for it in sec['items'] if not SKIP.match(it[0].strip())]
by_c = {}
for k, c in enumerate(am[:len(zi)]):
    by_c.setdefault(int(c), []).append(k)

lines = ['# 篇6 結界方法　鈔記對應清單', '', '共 %d 鈔、%d 記' % (len(chao), len(zi)), '']
for i, it in enumerate(chao, 1):
    ks = sorted(by_c.get(i, []))
    rng = ('記%d–%d' % (ks[0] + 1, ks[-1] + 1)) if ks else '（無記）'
    lines.append('| 鈔%02d | %s | %s | %s |' % (
        i, re.sub(r'\s+', '', it[0])[:38], rng,
        (zi[ks[0]][0][:34] if ks else '')))
head = ['| 鈔 | 鈔文起首 | 記範圍 | 首記起首 |', '|:--:|:--|:--:|:--|']
body = lines[4:]
out = os.path.join(B, '合編材料', '篇06_鈔記對應清單.md')
io.open(out, 'w', encoding='utf-8').write('\n'.join(lines[:4] + head + body) + '\n')
print('saved', out)
print('\n'.join(lines[:6]))
