import json, os
base=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
inp=json.load(open(os.path.join(base,"ys_punct_in.json"),encoding="utf-8"))
ex=json.load(open(os.path.join(base,"punct_work","v3_extract.json"),encoding="utf-8"))
M=set("，。、；：？！「」（）")
def nm(s): return "".join(c for c in s if c not in M)
rows=[]
ok=0; bad=[]
for bi,(k,paras) in enumerate(inp.items()):
    for pi,p in enumerate(paras):
        key=f"{bi}.{pi}"
        if key not in ex: continue
        c=ex[key]
        if nm(c)==nm(p) and c.strip()==c:
            ok+=1
            n=len(nm(p)); m=sum(1 for x in c if x in M)
            rows.append((m/n if n else 9, key, n, m))
        else:
            bad.append((key, nm(p)==nm(c), repr(c[:20])))
print("valid:",ok,"invalid:",len(bad))
for b in bad[:20]: print(b)
rows.sort()
out=[]
for r in rows[:15]:
    out.append(f"{r[1]} chars={r[2]} marks={r[3]} ratio={r[0]:.3f}")
open(os.path.join(base,"punct_work","lowmarks.txt"),"w",encoding="utf-8").write("\n".join(out))
print("low ratio list written")
