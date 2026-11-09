import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
def block(ch,seg):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    return bl[int(seg)-1]
targets=[("02a_卷上之下","52"),("02a_卷上之下","65"),("02b_卷上之下","1"),("02b_卷上之下","107"),("02b_卷上之下","120"),("03a_卷中之上","5")]
out=[]
for ch,s in targets:
    out.append(f"===== {ch} seg{s} len={len(block(ch,s))}")
    out.append(block(ch,s)); out.append("")
io.open("_g2man2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
