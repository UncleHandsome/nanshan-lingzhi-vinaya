import sys, io, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
def block(ch,seg):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    return bl[int(seg)-1]
for s in ["77","78"]:
    print("==== seg",s)
    print(block("01b_卷上之上",s))
    print()
