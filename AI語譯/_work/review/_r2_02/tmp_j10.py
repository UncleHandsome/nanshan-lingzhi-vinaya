# -*- coding: utf-8 -*-
import io, os, re, glob, collections, json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
J10=os.path.join(ROOT,"校閱_10K")
files=glob.glob(os.path.join(J10,"*.txt"))
nums=sorted(int(re.search(r"_(\d+)\.txt$",p).group(1)) for p in files)
tgt=[n for n in nums if n>=642]
pat=re.compile(r"【(\d{3})-(\d{4})】\s*([^#\r\n]+?)#(\d+)")
out=["nums=%d tgt=%d max=%d"%(len(nums),len(tgt),max(nums))]
allmap={}
for n in tgt:
    p=os.path.join(J10,"校閱_%03d.txt"%n)
    t=io.open(p,encoding="utf-8-sig",errors="replace").read()
    ms=pat.findall(t)
    d=collections.OrderedDict()
    for a,b,book,seg in ms:
        d[a+"-"+b]=(book.strip(),int(seg))
    books=collections.Counter(v[0] for v in d.values())
    allmap[str(n)]=d
    out.append("%d n_ids=%d tags=%d books=%s"%(n,len(d),len(ms),dict(books)))
io.open("tmp_j10.txt","w",encoding="utf-8").write("\n".join(out))
json.dump(allmap, io.open("tmp_j10.json","w",encoding="utf-8"), ensure_ascii=False)
