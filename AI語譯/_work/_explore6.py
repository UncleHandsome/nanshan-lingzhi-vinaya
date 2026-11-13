import json,os,collections
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
d=json.load(open(os.path.join(root,"blocks.json"),encoding="utf-8"))
c=collections.Counter((b["book"],b["chunk"]) for b in d)
print("chunks in blocks.json:",len(c))
for k in list(c)[:15]: print(k,c[k], "maxpara", max(b["para"] for b in d if (b["book"],b["chunk"])==k))
pc=json.load(open(os.path.join(root,"para_counts.json"),encoding="utf-8"))
for k in list(pc)[:10]: print("para_counts",k,pc[k])
