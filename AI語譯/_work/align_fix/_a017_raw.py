# -*- coding: utf-8 -*-
import io, os, re, json, importlib.util, sys
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections()
idx = 15
print('=== idx', idx, SECS[idx]['name'], 'raw items', len(SECS[idx]['items']))
for i, (o, t) in enumerate(SECS[idx]['items']):
    print('[%d] %s' % (i, o[:40]))
