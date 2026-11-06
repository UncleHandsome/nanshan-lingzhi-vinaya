# -*- coding: utf-8 -*-
"""產生卷首（序＋三十篇名＋十門）鈔/記對照輸入，供 AI 標鈔界"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '00_卷首.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
am0 = AM.get('0', [])
front = [(k + 1, ZI[0][k][0]) for k in range(len(ZI[0]))
         if (k < len(am0) and int(am0[k]) == 0)]
data = {
    'chao': [{'n': i + 1, 'text': t} for i, t in enumerate(sp)],
    'ji': [{'n': n, 'text': t[:1200]} for n, t in front],
}
fp = os.path.join(B, 'AI語譯', '_work', 'pian_inputs_11_30', '卷首.json')
json.dump(data, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
print('鈔首', len(sp), '記', len(front), '→', fp)
for i, t in enumerate(sp[:12]):
    print(i + 1, t[:40])
