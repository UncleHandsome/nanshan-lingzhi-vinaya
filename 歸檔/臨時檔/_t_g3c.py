import io, sys, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
def block(ch,seg):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    return bl[int(seg)-1].replace("\n","")
t=block("01a_卷上之上","35")
i=t.find("沒有戒場")
print("SEG35:",repr(t[i-20:i+120]))
t2=block("01b_卷上之上","85")
j=t2.find("式叉摩那被判定")
print("SEG85:",repr(t2[j-10:j+120]))
