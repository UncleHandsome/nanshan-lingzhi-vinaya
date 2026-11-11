import json,io,collections,os,sys
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0,OUT)
import _r2lib as L
M=L.load_map(); idx=M["idx"]
R=json.load(io.open(os.path.join(OUT,"_refs.json"),encoding="utf-8"))
by=R["by_chunk"]
per=collections.defaultdict(set)
for ch,pres in by.items():
    for p in pres:
        if not (550<=int(p)<=641): continue
        for g,d in R["refs"][p].items(): pass
# use refs directly
for ch,pres in by.items():
    for p in pres:
        if not (550<=int(p)<=641): continue
        for g in R["refs"][p]["all"]:
            if idx[g]["chunk"]==ch: per[ch].add(g)
tot=0
for ch in sorted(per,key=lambda s:s):
    ps=L.paras(ch)
    print(ch[:3], "segs=%d"%len(ps), "with_op=%d"%len(per[ch]), "missing=%d"%(len(ps)-len(per[ch])))
    tot+=len(per[ch])
print("TOTAL segments with opinions:",tot)
