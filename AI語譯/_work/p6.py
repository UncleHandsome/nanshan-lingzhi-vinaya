import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
parsed=json.load(open(r"AI語譯\_work\parsed.json",encoding="utf-8"))
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
bykey=collections.defaultdict(list)
for b in blocks: bykey[b["key"]].append(b)
def base(k):
    return re.sub(r'\s*[（(][^）)]*[）)]\s*$','',k).strip()
def find(key):
    b=base(key)
    if b in bykey: return b
    # try decreasing parenthetical strip
    for cand in [key, re.sub(r'\s*\(\d+\)$','',key).strip()]:
        if cand in bykey: return cand
    return None
yes=[e for e in parsed if e["verdict"]=="是錯"]
rows=[]
unresolved=[]
for e in yes:
    bb=find(e["key"])
    if not bb:
        unresolved.append(e["key"]); continue
    loc=bykey[bb][0]
    rows.append(dict(src=e["src"],key=e["key"],base=bb,book=loc["book"],chunk=loc["chunk"],para=loc["para"],
                     judge=e["judge"],sug=e["sug"],tag=e["tag"]))
print("resolved:",len(rows),"unresolved:",unresolved)
# dedupe by (book,chunk,para,sug)
seen={}; uniq=[]
for r in rows:
    k=(r["book"],r["chunk"],r["para"],r["sug"])
    if k in seen:
        seen[k].append(r["key"]); continue
    r["alias"]=[]; seen[k]=[]; uniq.append(r)
for r in uniq:
    r["alias"]=seen[(r["book"],r["chunk"],r["para"],r["sug"])]
print("unique (loc,sug):",len(uniq))
# load current paragraphs
cache={}
def para(book,chunk,n):
    p=os.path.join("AI語譯","out",book,chunk+".txt")
    if p not in cache:
        raw=open(p,encoding="utf-8",newline="").read()
        cache[p]=(raw, raw.split("\r\n"))
    raw,lines=cache[p]
    idx=2*n-1
    if idx-1<len(lines): return lines[idx-1]
    return None
for r in uniq:
    r["cur"]=para(r["book"],r["chunk"],r["para"])
json.dump(uniq, open(r"AI語譯\_work\work.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
stat=collections.Counter()
for r in uniq:
    cur=r["cur"]; sug=r["sug"]
    if cur is None: stat["OOB"]+=1; r["cls"]="OOB"; continue
    if cur.strip()==sug.strip(): r["cls"]="SAME"
    else:
        sm=difflib.SequenceMatcher(None,cur,sug)
        r["ratio"]=round(sm.ratio(),3)
        ops=[o for o in sm.get_opcodes() if o[0]!='equal']
        r["nops"]=len(ops)
        r["cls"]="NEAR" if sm.ratio()>=0.75 and len(ops)<=6 else "FAR"
    stat[r["cls"]]+=1
print(stat)
json.dump(uniq, open(r"AI語譯\_work\work.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
for r in sorted(uniq,key=lambda x:(x["cls"],x["book"],x["chunk"],x["para"])):
    print(f'{r["cls"]:<5} {r["base"]:<20} {r["book"]}/{r["chunk"]}#{r["para"]:<4} ratio={r.get("ratio","-")} nops={r.get("nops","-")} cur={len(r["cur"] or "")} sug={len(r["sug"])}')
