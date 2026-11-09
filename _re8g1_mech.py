import json, re
g1 = json.load(open(r"AI語譯\_work\review\_re8g1_rows.json", encoding="utf-8"))

def spans(s):
    # return balanced 「...」 spans as (start,end) inclusive of quotes
    res=[]; stack=[]
    for i,ch in enumerate(s):
        if ch=="「": stack.append(i)
        elif ch=="」":
            if stack:
                st=stack.pop()
                res.append((st,i))
    res.sort()
    return res

KW = ["修正為","改譯為","改為","改作","改標為","改寫為"]

def extract(s):
    sp = spans(s)
    pairs=[]
    for kw in KW:
        for m in re.finditer(kw, s):
            ks, ke = m.start(), m.end()
            # NEW span starting at ke
            new=None
            for (a,b) in sp:
                if a==ke:
                    new=(a,b); break
            if not new: continue
            # OLD span ending right before ks
            old=None
            for (a,b) in sp:
                if b==ks-1:
                    old=(a,b); break
            if old is None:
                # look for 將「...」 preceding
                pre = s[:ks]
                for (a,b) in sp:
                    if b<=ks and pre[max(0,a-2):a] in ("將","把") :
                        old=(a,b)
            if old is None: continue
            pairs.append((s[old[0]+1:old[1]], s[new[0]+1:new[1]], s[max(0,ks-20):ke+10]))
    # dedupe
    seen=set(); out=[]
    for p in pairs:
        if p[:2] in seen: continue
        seen.add(p[:2]); out.append(p)
    return out

stat={"rows":0,"mech":0,"fail":0}
detailed=[]
for r in g1:
    s=r[7]; cur=r[9]
    if not s.strip(): continue
    stat["rows"]+=1
    ps=extract(s)
    ok=[]
    for old,new,ctx in ps:
        if old and old in cur:
            ok.append((old,new))
    if ok:
        stat["mech"]+=1
    else:
        stat["fail"]+=1
    detailed.append({"gid":r[0],"chunk":r[2],"seg":r[3],"ok":ok,"n_all":len(ps),"S":s})
print(stat)
print("rows with >=1 pair extracted but none valid:", sum(1 for d in detailed if d["n_all"]>0 and not d["ok"]))
print("rows with 0 pair extracted:", sum(1 for d in detailed if d["n_all"]==0))
json.dump(detailed, open(r"AI語譯\_work\review\_re8g1_mech.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)
