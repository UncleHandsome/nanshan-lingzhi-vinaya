# -*- coding: utf-8 -*-
"""Generic dump: for a batch number, print full 記 items (with z) and full 鈔 cand (with c) plus out mapping."""
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
num = sys.argv[1]
sec = int(sys.argv[2]) if len(sys.argv) > 2 else None
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
SKIP1 = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2 = re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')
J = json.load(io.open(os.path.join(D, num + '.json'), encoding='utf-8'))
if sec is None:
    sec = J['sec']
C = [o for o, t in SECS[sec]['items'] if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
Z = ex.zitems_for(sec, ZS)
print('sec', sec, SECS[sec]['name'], 'C', len(C), 'Z', len(Z), 'items', len(J['items']), 'cand', len(J['cand']))
for it in J['items']:
    print('\n[z%d] %s' % (it['z'], Z[it['z']][0]))
print('\n===== CAND =====')
for cd in J['cand']:
    print('\n[c%d] %s' % (cd['c'], C[cd['c']]))
out = os.path.join(D, 'out_' + num + '.json')
if os.path.exists(out):
    print('\n===== OUT =====')
    M = json.load(io.open(out, encoding='utf-8'))['map']
    print(json.dumps([m['c'] for m in M]))
