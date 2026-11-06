# -*- coding: utf-8 -*-
"""Score z(900-1049) vs c(0-319) by shared character n-grams; show top candidates."""
import io, os, re, json, importlib.util, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS, ZS = ex.sections(), ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
IDX = 13
C = [o for o, t in SECS[IDX]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = [o for o, t in ex.zitems_for(IDX, ZS)]

def grams(s, n=3):
    h = re.sub(r'[^\u4e00-\u9fff]', '', s)
    return Counter(h[i:i+n] for i in range(0, max(0, len(h)-n+1)))

Cg = [grams(c) for c in C]
Zg = [grams(z) for z in Z]

def score(zg, cg):
    if not zg or not cg: return 0.0
    inter = sum((zg & cg).values())
    return inter

out = io.StringIO()
for z in range(900, 1050):
    sc = [(score(Zg[z], Cg[c]), c) for c in range(len(C))]
    sc.sort(reverse=True)
    top = sc[:6]
    out.write('[z%d] %s\n' % (z, ' | '.join('%d:%.2f' % (c, s) for s, c in top)))
io.open(os.path.join(AD, '_a012_top.txt'), 'w', encoding='utf-8').write(out.getvalue())
print(out.getvalue()[:3000])
