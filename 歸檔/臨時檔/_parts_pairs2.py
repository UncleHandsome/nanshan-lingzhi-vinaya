import json, re
rows = json.load(open("_parts_rows2.json",encoding="utf-8"))

def quotes(s):
    out=[]; stack=[]
    for i,ch in enumerate(s):
        if ch=="「": stack.append(i)
        elif ch=="」" and stack:
            st=stack.pop(); out.append((st,i,s[st+1:i]))
    out.sort(); return out

CONN = {"改為","改作","改成","改","作","應作","應改為","宜作","當作","改譯為","譯作","應譯為","改回","應為","宜改為","應改作","當改為","改稱","稱作","作「"}
res=[]
for r in rows:
    sug=r["suggestion"]
    qs=quotes(sug)
    pairs=[]
    for a in range(len(qs)):
        if a+1>=len(qs): break
        s1,e1,c1=qs[a]; s2,e2,c2=qs[a+1]
        mid=sug[e1+1:s2].strip()
        if mid in CONN or re.fullmatch(r"(?:應|宜|當|可)?(?:改|作|譯)(?:為|作)?", mid):
            pairs.append((c1,c2))
    r["_pairs2"]=pairs
json.dump(rows, open("_parts_rows3.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

from collections import Counter
cnt=Counter(); need=[]
for r in rows:
    ps=r["_pairs2"]
    if not ps: cnt["nopair"]+=1; need.append(r["idx"]); continue
    st=[(X,Y,r["current"].count(X),r["current"].count(Y)) for X,Y in ps]
    r["_st2"]=st
    if all(x>0 for _,_,x,_ in st): cnt["all-X"]+=1
    elif all(y>0 and x==0 for _,_,x,y in st): cnt["all-Y"]+=1
    else: cnt["mixed"]+=1; need.append(r["idx"])
print(cnt)
print("need:", need)
print("n need:", len(need))
tot=sum(len(r["problem"])+len(r["suggestion"])+len(r["current"]) for r in rows if r["idx"] in need)
print("chars for need:", tot)
