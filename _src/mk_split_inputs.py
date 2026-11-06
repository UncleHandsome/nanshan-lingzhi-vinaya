# -*- coding: utf-8 -*-
"""輸出篇1-5,7-10 的鈔/記清單，供 AI 標切點"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
OUT = os.path.join(B, 'AI語譯', '_work', 'pian_split_in')
os.makedirs(OUT, exist_ok=True)
for p in [1, 2, 3, 4, 5, 7, 8, 9, 10]:
    idx = p - 1
    sec = SECS[idx]
    zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
    by_c = {}
    for k, c in enumerate(am[:len(zi)]):
        c = int(c)
        if c > 0:
            by_c.setdefault(c, []).append(k)
    data = {
        'pian': p, 'name': sec['name'],
        'chao': [{'n': i + 1, 'text': t} for i, t in enumerate(chao)],
        'ji': [{'n': k + 1, 'c': int(am[k]) if k < len(am) else 0, 'text': zi[k][0]} for k in range(len(zi))],
    }
    fp = os.path.join(OUT, '篇%02d.json' % p)
    json.dump(data, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
    print(fp, '鈔', len(chao), '記', len(zi))
