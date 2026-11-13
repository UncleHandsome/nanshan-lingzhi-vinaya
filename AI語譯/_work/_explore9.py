import re,os
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def rl(p): return open(p,encoding="utf-8").read().splitlines()
def blocks(p):
    t=open(p,encoding="utf-8").read()
    return [b.strip() for b in re.split(r"\n\s*\n",t) if b.strip()]
print("== 戒疏: 疏/記 lines vs out blocks ==")
tot_src=0
for fn in sorted(os.listdir(os.path.join(root,"TXT_分卷","02_戒疏")))[:8]:
    s=os.path.splitext(fn)[0]
    lines=rl(os.path.join(root,"TXT_分卷","02_戒疏",fn))
    n=sum(1 for l in lines if l.startswith("【記】") or l.startswith("【疏】"))
    ob=blocks(os.path.join(root,"AI語譯","out","02_戒疏",s+".txt"))
    labeled=[b for b in ob if b.startswith("【記文】") or b.startswith("【疏文】")]
    print(f"{s:20s} src_marked={n:4d} out_blocks={len(ob):4d} labeled={len(labeled):4d}")
