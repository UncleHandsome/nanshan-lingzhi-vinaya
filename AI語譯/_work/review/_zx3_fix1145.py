# -*- coding: utf-8 -*-
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

o = L.Out('資持記', '08c_中二')
segs = list(o.segs)
# 1) 還原 seg18 被誤套的改動
i = 17
bad = '與上面第二犯緣相反（故不犯）出其餘兩種因緣是有罪的'
good = '反顯出其餘兩種因緣是有罪的'
assert segs[i].count(bad) == 1, segs[i].count(bad)
segs[i] = segs[i].replace(bad, good)
# 2) 套用到正確段 seg41
j = 40
old = '這五種因緣正好反顯前面的第二種犯戒因緣'
new = '這五種因緣正好與前面第二種犯緣相反（故不犯）'
assert segs[j].count(old) == 1, segs[j].count(old)
segs[j] = segs[j].replace(old, new)
o.segs = segs
o.save()

# 3) 修正 log_1145.json
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_zx3_log', 'log_1145.json')
d = json.load(open(p, encoding='utf-8'))
for e in d['edits']:
    if e['seg'] == 18 and '反顯' in e['old']:
        e['seg'] = 41
        e['old'] = old
        e['new'] = new
        e['why'] = '反＝相反（原誤植段18，已回改）'
d['relocs'] = []
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('fixed', len(segs))
