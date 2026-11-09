import json
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = {p['n']: p for p in json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))}
out = open(r'AI語譯/_work/review/_re4g2_chk.txt', 'w', encoding='utf-8')
for d in rows:
    p = plan[d['_n']]
    if p['kind'] != 'REPL_OK':
        continue
    a = p['a']
    if d['current'].count(a) != 1:
        continue
    out.write("### %d A=%s || B=%s\nP: %s\nS: %s\n\n" % (d['_n'], a, p['b'], d['problem'][:260], d['suggestion'][:260]))
out.close()
