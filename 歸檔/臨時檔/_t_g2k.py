import sys, json, io, os, difflib
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
for ch,seg in [("01a_卷上之上","22"),("01b_卷上之上","76")]:
    cur=[r[9] for r in rows if r[2]==ch and r[3]==seg][0]
    live=blocks(ch)[int(seg)-1]
    print("====",ch,seg,"report len",len(cur),"live len",len(live))
    sm=difflib.SequenceMatcher(None,cur,live)
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag!="equal":
            print(tag, "REP:",repr(cur[i1:i2])[:200], "| LIVE:",repr(live[j1:j2])[:200])
