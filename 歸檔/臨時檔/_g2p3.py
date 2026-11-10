import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
base=r"AI語譯\out\04_比丘尼鈔"
def block(ch,seg):
    txt=io.open(os.path.join(base,ch+".txt"),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    return bl[int(seg)-1]
targets=[("01b_卷上之上",x) for x in ["79","80","81","82","83","84","85","94"]]
out=[]
for ch,s in targets:
    out.append(f"===== {ch} seg{s} len={len(block(ch,s))}")
    out.append(block(ch,s))
    out.append("")
io.open("_g2man1.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
