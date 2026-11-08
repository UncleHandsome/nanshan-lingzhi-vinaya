import json, io
from collections import defaultdict
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
g=defaultdict(list)
for d in rows: g[(d['chunk'],d['seg'])].append(d['idx'])
for k,v in g.items():
    if len(v)>1: print(k,v)
