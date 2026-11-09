import json
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = {p['n']: p for p in json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))}
kinds = {'MANUAL'}
with open(r'AI語譯/_work/review/_re4g2_manual.txt','w',encoding='utf-8') as f:
    for d in rows:
        if plan[d['_n']]['kind'] not in kinds: continue
        f.write(f"### {d['_n']} | {d['gid']} | {d['chunk']} seg={d['seg']} {d['level']} {d['cls']}\n")
        f.write(f"P: {d['problem']}\n")
        f.write(f"S: {d['suggestion']}\n")
        f.write(f"C: {d['current']}\n\n")
