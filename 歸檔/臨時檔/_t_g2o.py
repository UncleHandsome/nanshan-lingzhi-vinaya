import sys, json, io, os, re
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
Q=re.compile(r"[「『“\"]([^」』”\"]{1,300})[」』”\"]")
pat_ab=re.compile(r"將[「『“\"]([^」』”\"]+)[」』”\"]\s*(?:一句)?(?:改|修正|修改)為[「『“\"]([^」』”\"]+)[」』”\"]")
out=[]
stat={"AB":0,"OTHER":0,"NOSUG":0}
for i,r in enumerate(rows):
    if "重複貼上" in r[6]: continue
    live=blocks(r[2])[int(r[3])-1]
    sug=r[7]
    if not sug.strip(): stat["NOSUG"]+=1; continue
    m=pat_ab.search(sug)
    if m:
        stat["AB"]+=1
        A,B=m.group(1),m.group(2)
        inA=A in live; inB=B in live
        out.append(f"{i}\tAB\tA_in_live={inA}\tB_in_live={inB}\t{r[2]}\t{r[3]}")
        out.append(f"   A={A[:120]}")
        out.append(f"   B={B[:120]}")
    else:
        stat["OTHER"]+=1
        out.append(f"{i}\tOTHER\t{r[2]}\t{r[3]}\tcls={r[5]}")
        out.append(f"   S={sug[:200]}")
print(stat)
io.open("_g2stat.txt","w",encoding="utf-8").write("\n".join(out))
