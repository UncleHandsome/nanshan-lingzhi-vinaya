# -*- coding: utf-8 -*-
import io, os, re, json
REV = os.path.dirname(os.path.abspath(__file__))
res = json.load(io.open(os.path.join(REV, '_g1b_sel.json'), encoding='utf-8'))
w = io.open(os.path.join(REV, '_g1b_cur.txt'), 'w', encoding='utf-8')
for i, x in enumerate(res, 1):
    w.write('### %d %s seg=%s\n%s\n\n' % (i, x['chunk'], x['seg'], x['out_para']))
w.close()
# search book for suspected mislocated strings
import glob
txt = {}
for p in glob.glob(os.path.join(REV, '..', '..', 'out', '02_戒疏', '*.txt')):
    txt[os.path.basename(p)] = io.open(p, encoding='utf-8').read()
probes = ['轉難', '勸學', '重聽', '不令他化', '不疊', '行醫師', '胸行師', '分為五個部分',
          '實重謂輕', '半滿犯重', '半衣邊', '是聖者起', '彼依其言', '俱舍', '為闕為畜',
          '多覓', '輕忽過惡', '半首', '參與', '龍公', '誦可至十三事', '百人長一人',
          '爭食奪命', '長十二肘', '人境', '重疊']
w2 = io.open(os.path.join(REV, '_g1b_probe.txt'), 'w', encoding='utf-8')
for p in probes:
    hits = [k for k, v in txt.items() if p in v]
    w2.write('%s -> %s\n' % (p, ', '.join(hits) if hits else 'NONE'))
w2.close()
print('ok')
