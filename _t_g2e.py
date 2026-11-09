import csv, sys, json, re
sys.stdout.reconfigure(encoding="utf-8")
rows = json.load(open("_g2rows.json", encoding="utf-8"))
QRE = re.compile(r"[「『“‘\"]([^」』”’\"]{1,200})[」』”’\"]")
def quotes(s):
    return [m.group(1) for m in QRE.finditer(s or "")]
def repdups(s):
    # find a repeated substring >=40 chars
    n=len(s)
    seen={}
    out=[]
    i=0
    for L in (60,40):
        pass
    # simple: hash 40-grams
    from collections import defaultdict
    d=defaultdict(list)
    for i in range(0,n-40):
        d[s[i:i+40]].append(i)
    best=None
    for k,v in d.items():
        if len(v)>1:
            best=(k,v[0],v[1]); break
    return best
for i,r in enumerate(rows):
    cur=r[9]; prob=r[6]; sug=r[7]
    q=quotes(prob); found=[x for x in q if x in cur]
    dup=repdups(cur)
    tag=""
    if not sug.strip(): tag="NOSUG"
    elif q and not found: tag="QS-NOTFOUND"
    elif dup: tag="HASDUP"
    print(f"{i:3d} {r[2]} s{r[3]} {r[4]} {r[5]} | q={len(q)} f={len(found)} | dup={bool(dup)} | {tag}")
    print("    P:", prob[:150])
    print("    S:", sug[:150])
