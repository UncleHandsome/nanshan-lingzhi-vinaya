import csv, sys, json, re
sys.stdout.reconfigure(encoding="utf-8")
rows = json.load(open("_g2rows.json", encoding="utf-8"))
def longest_rep(s):
    n=len(s); best=0; bi=(0,0)
    # suffix-automaton-free: check each length from large down using dict of 30-grams seeded
    from collections import defaultdict
    d=defaultdict(list)
    L=25
    for i in range(n-L+1):
        d[s[i:i+L]].append(i)
    cand=[(k,v) for k,v in d.items() if len(v)>1]
    if not cand: return 0
    # extend best
    k,v=cand[0]
    a,b=v[0],v[1]
    # extend match
    x=a+k.__len__(); y=b+k.__len__()
    while x<n and y<n and s[x]==s[y]:
        x+=1;y+=1
    return x-a
rep_rows=[r for r in rows if "重複" in r[6]]
print("重複 rows:", len(rep_rows))
for r in rep_rows:
    L=longest_rep(r[9])
    print(f"{r[2]} s{r[3]} len={len(r[9])} longest_rep={L}")
print()
# distribution of problem keywords
import collections
kw=collections.Counter()
for r in rows:
    if "重複" in r[6]: kw["重複"]+=1
    if "衍" in r[6] or "誤植" in r[6]: kw["衍誤"]+=1
print(kw)
