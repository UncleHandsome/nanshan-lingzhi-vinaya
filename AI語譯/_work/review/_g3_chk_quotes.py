import json, re, os
rows = json.load(open(r"AI語譯\_work\review\_g3_rows.json", encoding="utf-8"))
def paras(book, chunk):
    t = open(os.path.join(r"AI語譯","out",book,chunk+".txt"), encoding="utf-8").read().replace("\r\n","\n")
    return [x.strip() for x in re.split(r"\n\s*\n", t) if x.strip()]
cache={}
for i, r in enumerate(rows):
    key=(r["book"],r["chunk"])
    if key not in cache: cache[key]=paras(*key)
    ps=cache[key]; seg=int(r["seg"]); cur=r["current"]
    quotes=[q for q in re.findall(r"「([^」]{3,40})」", r["problem"])]
    hit=[q for q in quotes if q in cur]
    near=[]
    if quotes and not hit and seg-1 < len(ps):
        # where do quotes appear nearby?
        for off in (-2,-1,1,2):
            j=seg-1+off
            if 0<=j<len(ps) and any(q in ps[j] for q in quotes):
                near.append((seg+off, sum(1 for q in quotes if q in ps[j])))
    flag = "MISMATCH" if quotes and not hit else ""
    if flag or near:
        print(i, r["book"], r["chunk"], r["seg"], flag, "quotes", len(quotes), "hit", len(hit), "near", near)
