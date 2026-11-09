import json, re, sys
from difflib import SequenceMatcher
rows = json.load(open(r'AI語譯/_work/review/_re4g2_rows.json', encoding='utf-8'))

def norm(s):
    return re.sub(r'\s+', '', s)

def q(s):
    return re.findall(r'[「『](.*?)[」』]', s)

pat1 = re.compile(r'將[「『]([^」』]*)[」』](?:句)?改為[「『]([^」』]*)[」』]')
pat2 = re.compile(r'將(?:文末)?[「『]([^」』]*)[」』](?:句)?翻譯為[「『]([^」』]*)[」』]')
out = []
for d in rows:
    sug = d['suggestion'].strip()
    prob = d['problem'].strip()
    cur = d['current']
    rec = {'n': d['_n'], 'kind': None}
    if not sug:
        rec['kind'] = 'NOSUG'
    else:
        m = pat1.search(sug) or pat2.search(sug)
        if m:
            a, b = m.group(1), m.group(2)
            rec['a'] = a; rec['b'] = b
            if a in cur:
                rec['kind'] = 'REPL_OK'
            else:
                # fuzzy
                best = 0; besti = -1
                la = len(norm(a))
                for i in range(len(cur)):
                    # too slow for big; skip
                    pass
                rec['kind'] = 'REPL_MISS'
        else:
            rec['kind'] = 'MANUAL'
    out.append(rec)

from collections import Counter
print(Counter(r['kind'] for r in out))
json.dump(out, open(r'AI語譯/_work/review/_re4g2_plan.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
with open(r'AI語譯/_work/review/_re4g2_plan.txt','w',encoding='utf-8') as f:
    for r in out:
        f.write(f"{r['n']}\t{r['kind']}\tA={r.get('a','')}\tB={r.get('b','')}\n")
