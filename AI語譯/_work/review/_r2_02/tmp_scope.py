# -*- coding: utf-8 -*-
import io, os, re, glob, collections, json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
J10=os.path.join(ROOT,"校閱_10K"); R2=os.path.join(ROOT,"batch_qwen","r2")
pat=re.compile(r"【(\d{3})-(\d{4})】\s*([^#\r\n]+?)#(\d+)")
r2nums=sorted(int(re.search(r"resp_(\d+)",p).group(1)) for p in glob.glob(os.path.join(R2,"resp_*.txt")))
tgt=[n for n in r2nums if n>=642]
out=["r2 nums >=642: %d  range %d..%d"%(len(tgt),min(tgt),max(tgt))]
per={}
for n in tgt:
    p=os.path.join(J10,"校閱_%03d.txt"%n)
    if not os.path.exists(p):
        out.append("%d NO MATERIAL"%n); continue
    t=io.open(p,encoding="utf-8-sig",errors="replace").read()
    ms=pat.findall(t)
    d=collections.OrderedDict()
    for a,b,book,seg in ms:
        d[a+"-"+b]=(book.strip(),int(seg))
    per[str(n)]=d
    byb=collections.defaultdict(list)
    for k,v in d.items(): byb[v[0]].append(v[1])
    s="; ".join("%s segs %d-%d(n=%d)"%(b.split("/")[0]+"/"+b.split("/")[1][:3],min(v),max(v),len(v)) for b,v in byb.items())
    out.append("%d ids=%d | %s"%(n,len(d),s))
io.open("tmp_scope.txt","w",encoding="utf-8").write("\n".join(out))
json.dump(per, io.open("tmp_per.json","w",encoding="utf-8"), ensure_ascii=False)
