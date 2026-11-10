import json
rows = json.load(open("_parts_rows3.json",encoding="utf-8"))
cur = [l.rstrip("\n") for l in open("AI語譯/out/資持記/04d_上三.txt",encoding="utf-8")]
print("lines:",len(cur))
out=[]
for i in (43,44,45,46):
    r=[x for x in rows if x["idx"]==i][0]
    c=r["current"]
    hits=[k+1 for k,l in enumerate(cur) if l==c]
    hits0=[k for k,l in enumerate(cur) if l==c]
    out.append(f"idx{i} seg{r['seg']} exact-match lines(1based)={hits} (0based)={hits0} len={len(c)}")
open("_parts_align.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
