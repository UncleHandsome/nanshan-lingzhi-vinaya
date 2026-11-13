import re,os
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def rl(p): return open(p,encoding="utf-8").read().splitlines()
def blocks(p):
    t=open(p,encoding="utf-8").read()
    return [b.strip() for b in re.split(r"\n\s*\n",t) if b.strip()]
def model_paras(lines):
    ps=[l for l in lines[4:] if l.strip()]
    if ps and not ps[0].startswith("\u3000\u3000"): ps=ps[1:]
    return ps
print("== 鈔: model paras vs out blocks ==")
bad=0
for fn in sorted(os.listdir(os.path.join(root,"TXT_分卷","01_行事鈔"))):
    s=os.path.splitext(fn)[0]
    mp=model_paras(rl(os.path.join(root,"TXT_分卷","01_行事鈔",fn)))
    ob=blocks(os.path.join(root,"AI語譯","out","01_行事鈔",s+".txt"))
    ok = len(mp)==len(ob)
    if not ok: bad+=1
    print(f"{s:22s} model={len(mp):4d} out={len(ob):4d} {'OK' if ok else 'DIFF'}")
print("bad:",bad)
