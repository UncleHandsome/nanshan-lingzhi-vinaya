import json, re
g1 = json.load(open(r"AI語譯\_work\review\_re8g1_rows.json", encoding="utf-8"))

def spans(s):
    res=[]; stack=[]
    for i,ch in enumerate(s):
        if ch=="「": stack.append(i)
        elif ch=="」":
            if stack:
                st=stack.pop(); res.append((st,i))
    res.sort(); return res

def norm(x):
    return x.replace("『","「").replace("』","」")

KW=["修正為","改譯為","改標為","改寫為","改為","改作"]

def extract(s, cur):
    sp=spans(s); pairs=[]
    for kw in KW:
        for m in re.finditer(kw, s):
            ks,ke=m.start(),m.end()
            j=ke
            while j<len(s) and s[j] in "：:，、。 ": j+=1
            new=None
            for (a,b) in sp:
                if a==j: new=(a,b); break
            if not new: continue
            cands=[]
            for (a,b) in sp:
                if b==ks-1: cands.append((a,b))
            for (a,b) in sp:
                if b<ks and s[max(0,a-2):a] in ("將","把"): cands.append((a,b))
            for (a,b) in sp:
                if b<ks and ks-b<=22: cands.append((a,b))
            old=None
            for (a,b) in cands:
                cand=norm(s[a+1:b])
                if cand and cand in norm(cur): old=cand; break
            if old is None: continue
            pairs.append((old, norm(s[new[0]+1:new[1]]), kw))
    seen=set(); out=[]
    for o,n,k in pairs:
        if (o,n) in seen: continue
        seen.add((o,n)); out.append((o,n))
    return out

d=[]
for r in g1:
    if not r[7].strip(): continue
    ps=extract(r[7], r[9])
    d.append({"gid":r[0],"chunk":r[2],"seg":r[3],"level":r[4],"cls":r[5],"P":r[6],"S":r[7],"CUR":r[9],"pairs":ps})
auto=[x for x in d if len(x["pairs"])>=1]
print("rows w/ pairs", len(auto), "of", len(d))
print("single", sum(1 for x in auto if len(x["pairs"])==1))
print("no pairs", len(d)-len(auto))
json.dump(d, open(r"AI語譯\_work\review\_re8g1_ext2.json","w",encoding="utf-8"), ensure_ascii=False)
