def check(s):
    errs=[]
    for op,cl,name in [("「","」","quote"),("（","）","paren"),("『","』","dquote")]:
        depth=0
        for ch in s:
            if ch==op:
                depth+=1
                if depth>2: errs.append(name+" too deep")
            elif ch==cl:
                depth-=1
                if depth<0: errs.append(name+" close before open"); depth=0
        if depth!=0: errs.append(name+" unclosed")
    return errs
for n,line in enumerate(open("AI語譯/_work/review/fix_re8_g3.tsv",encoding="utf-8"),1):
    if not line.strip(): continue
    p=line.rstrip("\n").split("\t")
    e=check(p[3])
    if e: print(n,p[0],p[1],p[2],e)
print("done")
