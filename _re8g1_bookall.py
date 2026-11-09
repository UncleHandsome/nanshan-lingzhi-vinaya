import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
book={}
for ch in set(x["chunk"] for x in d):
    ls=[l for l in open(rf"AI語譯\out\03_業疏\{ch}.txt",encoding="utf-8").read().split("\n") if l.strip()]
    book[ch]=ls
same=0; diff=[]
for x in d:
    ls=book[x["chunk"]]
    cur=x["CUR"].strip()
    idx=int(x["seg"])-1
    if 0<=idx<len(ls) and ls[idx].strip()==cur:
        same+=1
    else:
        hit=[i for i,l in enumerate(ls) if l.strip()==cur]
        diff.append((x["gid"],x["chunk"],x["seg"],"idxdiff" if hit else "nomatch", hit[:2]))
print("rows same at idx:",same,"of",len(d))
print("diff rows:",len(diff))
for r in diff[:20]: print(" ",r)
