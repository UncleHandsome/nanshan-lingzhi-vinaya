import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
parsed=json.load(open(r"AI語譯\_work\parsed2.json",encoding="utf-8"))
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
bykey=collections.defaultdict(list)
for b in blocks: bykey[b["key"]].append(b)
def base(k): return re.sub(r'\s*[（(][^）)]*[）)]\s*$','',k).strip()
def find(key):
    for cand in [key, base(key), re.sub(r'\s*\(\d+\)$','',key).strip()]:
        if cand in bykey: return cand
    return None
yes=[e for e in parsed if e["verdict"]=="是錯"]
rows=[]
for e in yes:
    bb=find(e["key"]); loc=bykey[bb][0]
    rows.append(dict(src=e["src"],key=e["key"],base=bb,book=loc["book"],chunk=loc["chunk"],para=loc["para"],
                     judge=e["judge"],sug=(e["sug"] or "").strip(),tag=e["tag"],
                     mdt=bykey[bb][0]["trans"], origs=[b["orig"] for b in bykey[bb] if b["orig"]]))
# dedupe
seen=collections.OrderedDict()
for r in rows:
    seen.setdefault((r["book"],r["chunk"],r["para"],r["sug"]),[]).append(r)
uniq=[]
for k,v in seen.items():
    r=v[0].copy(); r["alias"]=[x["key"] for x in v[1:]]; uniq.append(r)
print("uniq",len(uniq))
# paragraph pool per file
files={}
def pool(book,chunk):
    key=(book,chunk)
    if key in files: return files[key]
    p=os.path.join("AI語譯","out",book,chunk+".txt")
    raw=open(p,encoding="utf-8",newline="").read()
    paras=[]; pos=0
    for seg in raw.split("\n"):
        paras.append((pos,seg)); pos+=len(seg)+1
    lst=[(i//2+1, off, s.rstrip("\r")) for i,(off,s) in enumerate(paras) if i%2==0]
    files[key]=(raw,lst); return files[key]
moved=0
for r in uniq:
    raw,lst=pool(r["book"],r["chunk"])
    best=None
    for n,off,txt in lst:
        sc=max(difflib.SequenceMatcher(None,txt,r["sug"]).ratio(),
               difflib.SequenceMatcher(None,txt,r["mdt"]).ratio() if r["mdt"] else 0)
        if best is None or sc>best[0]: best=(sc,n,off,txt)
    r["sc"],r["found"],r["off"],r["cur"]=best
    if r["found"]!=r["para"]: moved+=1; r["moved"]=True
    else: r["moved"]=False
print("relocated (different para):",moved)
print("low-score (<0.8):",[(r["base"],r["para"],r["found"],round(r["sc"],3)) for r in uniq if r["sc"]<0.8])
json.dump(uniq,open(r"AI語譯\_work\work2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for r in uniq:
    if r["moved"]: print(f'MOVE {r["base"]:<20} {r["book"]}/{r["chunk"]} declared#{r["para"]} found#{r["found"]} sc={r["sc"]:.3f}')
