import json, re
rows = json.load(open("_parts_rows.json",encoding="utf-8"))

def quotes(s):
    """return list of (start,end,content) for 「...」 with nesting"""
    out=[]; stack=[]
    for i,ch in enumerate(s):
        if ch=="「":
            stack.append(i)
        elif ch=="」" and stack:
            st=stack.pop()
            out.append((st,i,s[st+1:i]))
    out.sort()
    return out

pat = re.compile(r"改(?:為|作|成)")
res=[]
for r in rows:
    sug=r["suggestion"]
    qs=quotes(sug)
    pairs=[]
    # find quote followed by small text then 改為 then quote
    for a in range(len(qs)):
        for b in range(a+1,len(qs)):
            s1,e1,c1=qs[a]; s2,e2,c2=qs[b]
            mid=sug[e1+1:s2]
            if len(mid)<=6 and pat.search(mid):
                pairs.append((c1,c2))
                break
    r["_pairs"]=pairs
    r["_sugqs"]=[c for _,_,c in qs]
json.dump(rows, open("_parts_rows2.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

from collections import Counter
cnt=Counter()
amb=[]
for r in rows:
    if not r["_pairs"]:
        cnt["no-pair"]+=1; continue
    st=[]
    for X,Y in r["_pairs"]:
        xc=r["current"].count(X); yc=r["current"].count(Y)
        st.append((X,Y,xc,yc))
    r["_stat"]=st
    allx=all(xc>0 for _,_,xc,_ in st); ally=all(yc>0 for _,_,_,yc in st)
    if allx: cnt["X-present"]+=1
    elif ally: cnt["Y-present-only"]+=1
    else: cnt["ambiguous"]+=1; amb.append(r["idx"])
print(cnt)
print("ambiguous idx:", amb)
print("no-pair idx:", [r["idx"] for r in rows if not r["_pairs"]])
