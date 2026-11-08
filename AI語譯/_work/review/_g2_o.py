import json, io
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
for idx in [3]:
    r=[x for x in rows if x['idx']==idx][0]
    print('ORIG:',r['orig'])
    print('TR:',r['tr'][:200])
