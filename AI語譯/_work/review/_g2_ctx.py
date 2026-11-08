import json, io
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
d=[r for r in rows if r['idx']==7][0]
t=d['current']
for old,new in [("結界安居","結夏安居"),("相續結界而得成就","相續作法受安居而得成就"),("結界的白文","受安居的誓詞（結文）")]:
    t=t.replace(old,new)
i=0
while True:
    j=t.find('結界',i)
    if j<0: break
    print(repr(t[max(0,j-25):j+15]))
    i=j+1
