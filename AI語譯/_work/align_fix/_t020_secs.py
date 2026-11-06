# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZS = ex.zsecs()
for i, s in enumerate(SECS):
    print(i, s['name'], len(s['items']))
print('---zsecs---')
for i, s in enumerate(ZS):
    print(i, s['name'], len(s['items']))
