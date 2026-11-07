import json, os, re
base = r"AI語譯"
rows = json.load(open(r"AI語譯\_work\review\_g3_rows.json", encoding="utf-8"))
cache = {}
def paras(book, chunk):
    key=(book,chunk)
    if key not in cache:
        p=os.path.join(base,"out",book,chunk+".txt")
        t=open(p,encoding="utf-8").read().replace("\r\n","\n")
        cache[key]=[x.strip() for x in re.split(r"\n\s*\n",t) if x.strip()]
    return cache[key]
for i,r in enumerate(rows):
    ps=paras(r["book"],r["chunk"])
    seg=int(r["seg"])
    if seg>len(ps):
        print(i,"SEG OUT OF RANGE",len(ps),r["book"],r["chunk"],seg); continue
    p=ps[seg-1]
    cur=r["current"]
    if p!=cur:
        flat=p.replace("\n","")
        tag="TRUNC-NL" if cur==p.split("\n")[0] and "\n" in p else ("NL" if p.replace("\n","")==cur else "DIFF")
        print(i,tag,"len",len(cur),len(p),"nl",p.count("\n"),r["book"],r["chunk"],seg)
