# -*- coding: utf-8 -*-
"""對已套用的 log 追加單筆修訂（不重寫整檔 log）。"""
import os, sys, io, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2a_lib as L

n = int(sys.argv[1])
chunk = sys.argv[2]
seg = int(sys.argv[3])
old = sys.argv[4]
new = sys.argv[5]
why = sys.argv[6] if len(sys.argv) > 6 else ''

o = L.Out('03_業疏', chunk)
t = o.segs[seg - 1]
c = t.count(old)
assert c == 1, 'COUNT=%d %r' % (c, old)
o.segs[seg - 1] = t.replace(old, new)
o.save()

lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_r2c_log', 'log_%d.json' % n)
d = json.load(open(lp, encoding='utf-8'))
d['edits'].append(dict(book='03_業疏', chunk=chunk, seg=seg, old=old, new=new, why=why))
json.dump(d, open(lp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('appended %d seg%d %s' % (n, seg, chunk))
