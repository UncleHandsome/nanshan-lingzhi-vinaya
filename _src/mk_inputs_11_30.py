# -*- coding: utf-8 -*-
"""整理篇11-30 的會本輸入資料與提示詞"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
OUT = os.path.join(B, 'AI語譯', '_work', 'pian_inputs_11_30')
os.makedirs(OUT, exist_ok=True)

rows = []
for p in range(11, 31):
    idx = p - 1
    sec = SECS[idx]
    zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
    data = {
        'pian': p, 'name': sec['name'],
        'chao': [{'n': i + 1, 'text': t} for i, t in enumerate(chao)],
        'ji': [{'n': k + 1, 'text': zi[k][0],
                'c_hint': int(am[k]) if k < len(am) else 0} for k in range(len(zi))],
    }
    fp = os.path.join(OUT, '篇%02d.json' % p)
    json.dump(data, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
    rows.append((p, sec['name'], len(chao), len(zi)))

print('%-4s %-10s %5s %5s' % ('篇', '名稱', '鈔', '記'))
for r in rows:
    print('%-4d %-10s %5d %5d' % r)
print('輸出', OUT)
