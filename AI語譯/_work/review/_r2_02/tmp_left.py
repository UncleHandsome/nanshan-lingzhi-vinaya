# -*- coding: utf-8 -*-
import io, os, re, json, collections
import _r2b as B
TOK="13a,13b,14a,14b,14c,15a,15b,15c,15d,16a,16b,16c,17a,17b,17c,18a,18b,18c,19a,19b,19c,19d,20a,20b,20c,21a,21b,21c".split(",")
out=[]; tot=0
for tok in TOK:
    chunk=B.fullname(tok); ps=B.paras(chunk)
    files=sorted(int(k) for k in B.PER if any(v[0].split("/")[1]==chunk for v in B.PER[k].values()))
    claims=[]; un=0
    for n in files:
        d=B.PER[str(n)]; segs_of={v[1] for v in d.values() if v[0].split("/")[1]==chunk}
        t=io.open(os.path.join(B.R2,"resp_%d.txt"%n),encoding="utf-8-sig",errors="replace").read()
        for b in [x.strip() for x in re.split(r"\n\s*\n",t) if x.strip()]:
            segs=[]
            for mm in re.finditer(r"(\d{3})-(\d{4})",b):
                k=mm.group(1)+"-"+mm.group(2)
                if k in d and d[k][0].split("/")[1]==chunk: segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"【(\d{4})】",b):
                    k=str(n)+"-"+mm.group(1)
                    if k in d and d[k][0].split("/")[1]==chunk: segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"(?<![\d-])(\d{4})(?![\d-])",b):
                    k=str(n)+"-"+mm.group(1)
                    if k in d and d[k][0].split("/")[1]==chunk: segs.append(d[k][1])
            quotes=B.QUOTE.findall(b)
            if not segs and quotes:
                for q in quotes:
                    hit=[i+1 for i,p in enumerate(ps) if q in p]
                    if len(hit)==1: segs.append(hit[0]); break
            sc=len(B.STRONG.findall(b))
            if sc==0: continue
            if not segs: un+=1; continue
            match=0
            for s in set(segs):
                if 0<s<=len(ps) and any(q in ps[s-1] for q in quotes): match=1; break
            claims.append((match,sc,n,sorted(set(segs)),b))
    merged=collections.OrderedDict()
    for m,sc,n,segs,b in claims:
        key=(n,re.sub(r"\s+","",b)[:120])
        if key in merged:
            o=merged[key]; merged[key]=(max(o[0],m),max(o[1],sc),n,sorted(set(o[3])|set(segs)),b)
        else: merged[key]=(m,sc,n,segs,b)
    ranked=sorted(merged.values(), key=lambda x:(-x[0],-x[1],x[3][0]))
    rest=ranked[5:]
    tot+=len(rest)
    out.append("#### %s  剩餘 %d 條（已核前5條）"%(tok,len(rest)))
    for m,sc,n,segs,b in rest:
        out.append("[%s] resp_%d %s score=%d | %s"%("LIVE" if m else "quote?",n,",".join("#%d"%s for s in segs),sc,re.sub(r"\s+"," ",b)[:110]))
    out.append("")
io.open("_r2b_leftover.txt","w",encoding="utf-8").write("\n".join(out))
print("leftover",tot,"lines",len(out))
