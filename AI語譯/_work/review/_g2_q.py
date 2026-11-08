import json, io
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
for idx in [15,32,64,65]:
    t=[r for r in rows if r['idx']==idx][0]['current']
    print(idx,'START',repr(t[:30]))
    print(idx,'END  ',repr(t[-40:]))
