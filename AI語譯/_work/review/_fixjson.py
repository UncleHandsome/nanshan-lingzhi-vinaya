# -*- coding: utf-8 -*-
import json
p = '_zx1389_e/1429.json'
s = open(p, encoding='utf-8').read()
s = s.replace('"why":"補明"],', '"why":"補明"},')
open(p, 'w', encoding='utf-8').write(s)
d = json.loads(s)
print('1429 edits', len(d['edits']))
p2 = '_zx1389_e/1430.json'
s2 = open(p2, encoding='utf-8').read()
try:
    d2 = json.loads(s2)
    print('1430 edits', len(d2['edits']))
except Exception as e:
    print('1430 err', e)
