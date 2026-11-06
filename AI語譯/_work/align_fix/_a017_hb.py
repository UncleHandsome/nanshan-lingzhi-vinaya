# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'align_fix')
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
HB = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
for k in sorted(HB, key=int):
    i = int(k)
    try:
        Z = ex.zitems_for(i, ZS)
        nz = len(Z)
    except Exception as e:
        nz = 'ERR'
    name = SECS[i]['name'] if i < len(SECS) else '?'
    print('key %-3s n=%-5d Zlen=%-5s name=%s' % (k, len(HB[k]), nz, name))
print()
# print alignment for sec16
for key in ('15', '16'):
    if key in HB:
        i = int(key)
        Z = ex.zitems_for(i, ZS)
        print('--- key', key, SECS[i]['name'], 'len', len(HB[key]), 'Zlen', len(Z))
        print(HB[key])
