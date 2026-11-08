import json, io
rows = json.load(io.open('AI語譯/_work/review/_g2_rows.json', encoding='utf-8'))
with io.open('AI語譯/_work/review/_g2_full.txt','w',encoding='utf-8') as f:
    for d in rows:
        f.write(f"@@@ idx={d['idx']} gid={d['gid']} chunk={d['chunk']} seg={d['seg']} level={d['level']} cls={d['cls']}\n")
        f.write("[P] " + d['problem'] + "\n")
        f.write("[S] " + d['suggestion'] + "\n")
        f.write("[C] " + d['current'] + "\n\n")
print('done')
