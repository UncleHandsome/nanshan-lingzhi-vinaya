import re
bad=[]
for i,line in enumerate(open("AI語譯/_work/review/fix_parts_g1.tsv",encoding="utf-8"),1):
    p=line.rstrip("\n").split("\t")
    t=p[3]
    chk=[]
    for pat,label in [(r"。。","double-period"),(r"，，","double-comma"),(r"、、","double-dun"),(r"^\W","starts-punct"),(r"（）","empty-paren"),(r"「」","empty-quote"),(r"〔〕","empty-bracket"),(r"的的|了了|是是","dup-word")]:
        if re.search(pat,t): chk.append(label)
    if chk: bad.append((i,p[1],p[2],chk,t[:40]))
print("suspicious:",len(bad))
for b in bad[:20]: print(b)
