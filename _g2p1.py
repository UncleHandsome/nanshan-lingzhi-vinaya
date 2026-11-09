import sys, json, io, os, re
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
pat_ab=re.compile(r"將[「『“\"]([^」』”\"]+)[」』”\"]\s*(?:一句)?(?:改|修正|修改)為[「『“\"]([^」』”\"]+)[」』”\"]")
auto=[]; manual=[]
for i,r in enumerate(rows):
    if "重複貼上" in r[6]: continue
    if not r[7].strip(): manual.append((i,"NOSUG")); continue
    live=blocks(r[2])[int(r[3])-1]
    m=pat_ab.search(r[7])
    if m:
        A,B=m.group(1),m.group(2)
        if B in live:
            auto.append((i,r[2],r[3],"SKIP-applied",A,B)); continue
        n=live.count(A)
        if n==1 and A in live:
            auto.append((i,r[2],r[3],"APPLY",A,B)); continue
        manual.append((i,f"AB count={n} lenA={len(A)}"))
    else:
        manual.append((i,"OTHER"))
print("auto", len(auto), "manual", len(manual))
from collections import Counter
print(Counter(x[3] for x in auto))
json.dump([list(x) for x in auto], open("_g2auto.json","w",encoding="utf-8"), ensure_ascii=False)
json.dump([[i,t] for i,t in manual], open("_g2manual.json","w",encoding="utf-8"), ensure_ascii=False)
print("manual rows:", [ (i,t) for i,t in manual])
