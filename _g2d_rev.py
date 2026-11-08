import csv, io
SRC = r"AI語譯/_work/review/report_dir.tsv"
rows=[]
with open(SRC,"r",encoding="utf-8",newline="") as f:
    r=csv.reader(f,delimiter="\t"); hdr=next(r)
    for rec in r:
        if not rec or rec==[""]: continue
        rows.append(dict(zip(hdr,rec)))
sel=[x for x in rows if x["book"] in {"資持記","05_拾毗尼義鈔"}]
outs=[l.split("\t") for l in io.open(r"AI語譯/_work/review/fix_dir_g2.tsv",encoding="utf-8").read().split("\n") if l]
rep=[]
for i,(x,o) in enumerate(zip(sel,outs)):
    cur=x["current"]; new=o[3]
    if i<48 or i>82:
        # locate first difference region
        k=0
        while k<min(len(cur),len(new)) and cur[k]==new[k]: k+=1
        # find tail match
        a=len(cur); b=len(new)
        while a>0 and b>0 and cur[a-1]==new[b-1] and a>k and b>k:
            a-=1; b-=1
        rep.append("ROW %d gid=%s %s seg=%s" % (i,x["gid"],x["chunk"],x["seg"]))
        rep.append("  CTX : ..."+new[max(0,k-45):k].replace("\n","")+"【"+new[k:b]+"】"+new[b:b+45]+"...")
        rep.append("  CUT : %r" % (cur[k:a],))
        rep.append("  ADD : %r" % (new[k:b],))
        rep.append("")
    else:
        rep.append("ROW %d gid=%s %s seg=%s [reassigned] cur=%d new=%d" % (i,x["gid"],x["chunk"],x["seg"],len(cur),len(new)))
        rep.append("  HEAD: "+new[:70])
        rep.append("  TAIL: "+new[-45:])
        rep.append("")
io.open("_g2d_review.txt","w",encoding="utf-8").write("\n".join(rep))
print("ok")
