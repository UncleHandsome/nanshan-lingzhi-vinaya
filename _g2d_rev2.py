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
for i in (48,49,50):
    cur=sel[i]["current"]; new=outs[i][3]
    k=0
    while k<min(len(cur),len(new)) and cur[k]==new[k]: k+=1
    a,b=len(cur),len(new)
    while a>0 and b>0 and cur[a-1]==new[b-1] and a>k and b>k:
        a-=1; b-=1
    rep.append("ROW %d gid=%s" % (i, sel[i]["gid"]))
    rep.append("  CTX : ..."+new[max(0,k-60):k]+"【"+new[k:b]+"】"+new[b:b+60]+"...")
    rep.append("  CUT : %r" % (cur[k:a],))
    rep.append("")
io.open("_g2d_review2.txt","w",encoding="utf-8").write("\n".join(rep))
print("ok")
