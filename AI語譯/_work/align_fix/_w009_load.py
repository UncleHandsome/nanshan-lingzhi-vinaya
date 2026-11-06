# -*- coding: utf-8 -*-
"""載入 sec14 全文（記/鈔）與現有 hb_align 對齊，供人工判讀。"""
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
idx = 13
C = [o for o, t in SECS[idx]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = ex.zitems_for(idx, ZS)
json.dump({'cao': C, 'ji': [o for o, t in Z]},
          io.open(os.path.join(D, '_w009_data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('sec', SECS[idx]['name'], 'C', len(C), 'Z', len(Z))
try:
    AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
    am = AM.get(str(idx)) or []
    print('hb_align len', len(am))
except Exception as e:
    am = []
    print('hb_align ERR', e)
# dump 記 z440..610 with current c
with io.open(os.path.join(D, '_w009_ji.txt'), 'w', encoding='utf-8') as f:
    for z in range(430, min(640, len(Z))):
        c = am[z] if z < len(am) else None
        f.write('[z%d|cur c%s] %s\n\n' % (z, c, Z[z][0]))
with io.open(os.path.join(D, '_w009_cao.txt'), 'w', encoding='utf-8') as f:
    for c in range(50, min(110, len(C))):
        f.write('[c%d] %s\n\n' % (c, C[c]))
print('dump ok')
