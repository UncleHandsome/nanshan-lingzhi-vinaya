import json,io,collections,re,os
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
rows=json.load(io.open(os.path.join(ROOT,"AI語譯","_work","review","_r2_02","_items_all.json"),encoding="utf-8"))
NEG=re.compile(r"無誤|無問題|正確|妥當|無需|不必|不需|均可|皆可|無礙|允當|貼切|精準|未見問題|沒有問題|無須")
def claim(r):
    if not r["claim"]: return False
    if NEG.search(r["text"]) and not re.search(r"建議|應作|宜改|改為|問題：",r["text"]): return False
    return True
rows=[r for r in rows if r["ids"]]
print("total item-id pairs:",sum(len(r["ids"]) for r in rows))
sel=[r for r in rows if claim(r)]
print("claim rows:",len(sel),"pairs:",sum(len(r["ids"]) for r in sel),"chars:",sum(len(r["text"]) for r in sel))
# dedupe identical text
seen={}
for r in sel:
    k=r["text"]
    if k not in seen: seen[k]=r
print("unique texts:",len(seen),"chars:",sum(len(k) for k in seen))
# per chunk unique segs and chars
per=collections.defaultdict(lambda: collections.defaultdict(list))
for r in sel:
    for g in r["ids"]: per[g[:3]][g].append(r)
for k in sorted(per):
    segs=per[k]
    ch=sum(len(x["text"]) for v in segs.values() for x in v)
    print(k,"segs=%d rows=%d chars=%d"%(len(segs),sum(len(v) for v in segs.values()),ch))
