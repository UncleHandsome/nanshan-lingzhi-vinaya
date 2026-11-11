# -*- coding: utf-8 -*-
import io, os, re, glob, json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
R2=os.path.join(ROOT,"batch_qwen","r2")
J10=os.path.join(ROOT,"校閱_10K")
files=sorted(glob.glob(os.path.join(R2,"resp_*.txt")), key=lambda p:int(re.search(r"resp_(\d+)",p).group(1)))
nums=[int(re.search(r"resp_(\d+)",p).group(1)) for p in files]
target=[n for n in nums if n>=642]
lines=[]
lines.append("total resp %d, nums %d..%d, >=642: %d"%(len(nums),min(nums),max(nums),len(target)))
missing10=[n for n in target if not os.path.exists(os.path.join(J10,"校閱_%03d.txt"%n))]
lines.append("校閱_10K missing for target: %d  first20=%s"%(len(missing10),missing10[:20]))
# scan tags
rows={}
books={}
for n in target:
    p=os.path.join(R2,"resp_%d.txt"%n)
    t=io.open(p,encoding="utf-8-sig",errors="replace").read()
    ids=set(re.findall(r"(\d{3})-(\d{4})",t))
    bs=set()
    for mm in re.finditer(r"【(\d{3})-(\d{4})】([^#<\n]{0,20})#",t):
        bs.add(mm.group(3).strip())
    books[n]=sorted(bs)
    rows[n]=(len(t),len(ids),sorted(bs)[:3])
for n in target:
    lines.append("%d len=%d ids=%d books=%s"%(n,rows[n][0],rows[n][1],",".join(rows[n][2])))
io.open("tmp_scan642.txt","w",encoding="utf-8").write("\n".join(lines))
