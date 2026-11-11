import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
work=json.load(open(r"AI語譯\_work\work.json",encoding="utf-8"))
def load(path):
    raw=open(path,encoding="utf-8",newline="").read()
    lines=[]; pos=0
    for seg in raw.split("\n"):
        lines.append((pos,seg)); pos+=len(seg)+1
    return raw,lines
cache={}
def getpara(book,chunk,n):
    p=os.path.join("AI語譯","out",book,chunk+".txt")
    if p not in cache: cache[p]=load(p)
    raw,lines=cache[p]
    idx=2*n-2   # 0-based line index for paragraph n
    if idx>=len(lines): return None,None
    off,seg=lines[idx]
    return seg.rstrip("\r"), (off,len(seg.rstrip("\r")))
stat=collections.Counter(); oob=[]
for r in work:
    cur,span=getpara(r["book"],r["chunk"],r["para"])
    r["cur"]=cur; r["span"]=span
    if cur is None: r["cls"]="OOB"; oob.append((r["base"],r["book"],r["chunk"],r["para"])); continue
    sug=r["sug"].strip()
    c=cur.strip()
    if c==sug: r["cls"]="SAME"
    else:
        sm=difflib.SequenceMatcher(None,c,sug); r["ratio"]=round(sm.ratio(),4)
        ops=[o for o in sm.get_opcodes() if o[0]!='equal']; r["nops"]=len(ops)
        r["cls"]="NEAR" if sm.ratio()>=0.9 else ("MID" if sm.ratio()>=0.6 else "FAR")
    stat[r["cls"]]+=1
print(stat)
print("OOB:",oob)
json.dump(work, open(r"AI語譯\_work\work.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
for r in sorted(work,key=lambda x:(x["cls"],x["book"],x["chunk"],x["para"])):
    print(f'{r["cls"]:<4} {r["base"]:<20} {r["book"]}/{r["chunk"]}#{r["para"]:<4} ratio={r.get("ratio","-")} nops={r.get("nops","-")} cur={len(r["cur"] or "")} sug={len(r["sug"])}')
