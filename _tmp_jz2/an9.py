# -*- coding: utf-8 -*-
import io, re, collections
import importlib.util, sys
spec = importlib.util.spec_from_file_location("a2", r"C:\Users\lionc\OneDrive\桌面\XW\三大部\_tmp_jz2\analyze2.py")
a2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a2)
rows = a2.load_pairs(); rows, anchors = a2.units_of(rows)
cnt = collections.Counter(r['u'] for r in rows if r['kind']=='鈔')
multi = [(u, c) for u, c in sorted(cnt.items()) if c > 1]
print('多鈔段單元:', multi)
print('單鈔段單元數:', sum(1 for u,c in cnt.items() if c==1), ' 總單元:', len(cnt))
# 檢查「記早於本戒鈔」的情形
bad2 = []
for u in range(1, len(a2.UNIT)+1):
    cs = [i for i,r in enumerate(rows) if r['kind']=='鈔' and r['u']==u]
    js = [i for i,r in enumerate(rows) if r['kind']=='記' and r['u']==u]
    if cs and js:
        early = [j for j in js if j < cs[0]]
        if early:
            bad2.append((u, a2.UNIT[u-1][0], [(rows[j]['num'], rows[j]['sub']) for j in early]))
print('記早於本戒鈔:', bad2)
