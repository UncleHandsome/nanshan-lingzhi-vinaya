import sys, json, io, os, difflib
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def blocks(ch):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    return [b.strip() for b in txt.split("\n\n") if b.strip()]
targets=[("01a_卷上之上","22"),("01b_卷上之上","76"),("02a_卷上之下","65"),("02b_卷上之下","88"),("03a_卷中之上","74"),("03b_卷中之上","32"),("04a_卷中之下","33"),("04b_卷中之下","19")]
out=[]
for ch,seg in targets:
    cur=[r[9] for r in rows if r[2]==ch and r[3]==seg][0]
    live=blocks(ch)[int(seg)-1]
    out.append(f"==== {ch} seg{seg} reportlen={len(cur)} livelen={len(live)}")
    sm=difflib.SequenceMatcher(None,cur,live)
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag!="equal":
            out.append(f"  {tag} @{i1}\n    REP: {cur[max(0,i1-25):i2+25]}\n    LIV: {live[max(0,j1-25):j2+25]}")
    for r in [x for x in rows if x[2]==ch and x[3]==seg]:
        out.append("  ROW prob: "+r[6][:180])
        out.append("      sug: "+r[7][:180])
    out.append("")
io.open("_g2diff8.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
