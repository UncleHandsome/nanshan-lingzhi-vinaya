import csv, json, re, sys
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
# classify: applied if problem sentence no longer in current
def norm(s):
    return re.sub(r'\s+', '', s)

stats = {'nosug':0, 'applied':0, 'todo':0}
lines = []
for d in rows:
    sug = d['suggestion'].strip()
    prob = d['problem'].strip()
    cur = d['current']
    tag = 'TODO'
    if not sug:
        tag='NOSUG'; stats['nosug']+=1
    else:
        # find quoted sentence in problem
        pieces = re.findall(r'[「『](.*?)[」』]', prob)
        pieces = [p for p in pieces if len(p) >= 6]
        # only consider quoted pieces that are not in current
        cand = [p for p in pieces if norm(p) not in norm(cur)]
        if pieces and len(cand)==len(pieces) and all(len(p)>=6 for p in pieces):
            # all quoted references gone -> applied
            if any(norm(p) in norm(d['tr']) for p in pieces) or True:
                tag='APPLIED?'
        stats['todo']+=1
    d['_tag']=tag
json.dump(rows, open(r'AI語譯/_work/review/_re4g2_rows.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(r'AI語譯/_work/review/_re4g2_dump.txt','w',encoding='utf-8') as f:
    for d in rows:
        f.write(f"### {d['_n']} | {d['gid']} | {d['book']} | {d['chunk']} | seg={d['seg']} | {d['level']} | {d['cls']}\n")
        f.write(f"PROBLEM: {d['problem']}\n")
        f.write(f"SUG: {d['suggestion']}\n")
        f.write(f"ORIG: {d['orig']}\n")
        f.write(f"TR: {d['tr']}\n")
        f.write(f"CUR: {d['current']}\n\n")
print(stats)
