import sys, json, io, os, re
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
manual=[tuple(x) for x in json.load(open("_g2manual.json",encoding="utf-8"))]
pat2=re.compile(r"[「『“\"]([^」』”\"]+)[」』”\"]\s*(?:一句)?(?:應?改為|修正為|修改為|改作|改)[：:]?\s*[「『“\"]([^」』”\"]+)[」』”\"]")
res=[]; left=[]
for i,t in manual:
    r=rows[i]
    if t=="NOSUG": left.append((i,"NOSUG")); continue
    live=blocks(r[2])[int(r[3])-1]
    m=pat2.search(r[7])
    if m:
        A,B=m.group(1),m.group(2)
        n=live.count(A)
        if n==1: res.append([i,r[2],r[3],A,B]); continue
        if A not in live and B in live: left.append((i,"SKIP-applied-2")); continue
        left.append((i,f"count={n}")); continue
    left.append((i,"nomatch"))
print("resolved", len(res), "left", len(left))
json.dump(res, open("_g2auto2.json","w",encoding="utf-8"), ensure_ascii=False)
json.dump([[i,t] for i,t in left], open("_g2manual2.json","w",encoding="utf-8"), ensure_ascii=False)
for i,t in left: print(i,t, rows[i][2], "seg"+rows[i][3], "|", rows[i][7][:110])
