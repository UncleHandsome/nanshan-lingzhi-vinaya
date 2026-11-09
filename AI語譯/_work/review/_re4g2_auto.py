import json, re
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))
plan = json.load(open(r'AI語譯/_work/review/_re4g2_plan.json', encoding='utf-8'))
pmap = {p['n']: p for p in plan}
def ctx(s, i, L, R=60):
    return s[max(0,i-L):i] + '⟦' + s[i:i+len('')] + '⟧'
with open(r'AI語譯/_work/review/_re4g2_auto.txt','w',encoding='utf-8') as f:
    for d in rows:
        p = pmap[d['_n']]
        if p['kind'] != 'REPL_OK': continue
        cur = d['current']; a = p['a']; b = p['b']
        c = cur.count(a)
        idxs = [m.start() for m in re.finditer(re.escape(a), cur)]
        f.write(f"### {d['_n']} cnt={c} len={len(cur)}\nA: {a}\nB: {b}\n")
        for i in idxs[:3]:
            f.write(f"  ctx: ...{cur[max(0,i-70):i]} [[{a}]] {cur[i+len(a):i+len(a)+70]}...\n")
        f.write("\n")
