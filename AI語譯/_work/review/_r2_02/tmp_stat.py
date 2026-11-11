# -*- coding: utf-8 -*-
import io, os, json, collections
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
OUTD=os.path.join(ROOT,"AI語譯","out","02_戒疏")
BAK=os.path.join(ROOT,"歸檔","r2修正前","02_戒疏")
rows=[]; per=collections.Counter(); segs=collections.defaultdict(set)
for line in io.open(os.path.join(HERE,"_apply2_log.jsonl"),encoding="utf-8"):
    line=line.strip()
    if not line: continue
    o=json.loads(line); rows.append(o); per[o["chunk"]]+=1; segs[o["chunk"]].add(o["seg"])
# tsv
def paras(chunk):
    t=io.open(os.path.join(OUTD,chunk+".txt"),encoding="utf-8",newline="").read()
    ps=t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"): ps[-1]=ps[-1][:-2]
    return ps
out=[]
for o in rows:
    ps=paras(o["chunk"]); out.append("%s\t%s\t%d\t%s"%(o["chunk"].split("_")[0],o["chunk"],o["seg"],ps[o["seg"]-1].replace("\t"," ")))
io.open(os.path.join(HERE,"fix_r2_02b.tsv"),"w",encoding="utf-8").write("\n".join(out)+"\n")
# stats
tb=sum(os.path.getsize(os.path.join(BAK,c+".txt")) for c in per)
print("repl",len(rows),"paras",sum(len(v) for v in segs.values()),"chunks",len(per),"bakbytes",tb)
print("bak files",len([f for f in os.listdir(BAK) if f.endswith(".txt")]))
print("chunk repl", dict(per))
