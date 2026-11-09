import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
def block(ch,seg):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    return bl[int(seg)-1]
targets=[("03b_卷中之上","3"),("03b_卷中之上","4"),("03b_卷中之上","6"),("03b_卷中之上","23"),("03b_卷中之上","24"),("03b_卷中之上","26"),("03b_卷中之上","27"),("04a_卷中之下","10"),("04a_卷中之下","23"),("04a_卷中之下","30")]
out=[]
for ch,s in targets:
    out.append(f"===== {ch} seg{s} len={len(block(ch,s))}")
    out.append(block(ch,s)); out.append("")
io.open("_g2man3.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
