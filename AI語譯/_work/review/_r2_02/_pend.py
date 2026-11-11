import os,io,json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
M=json.load(io.open(os.path.join(OUT,"_refs.json"),encoding="utf-8"))
done={"09b","09c","09d","10a","10b","10c","10d","11a","11b","11c","12a","12b"}
rows=[]
for k in sorted(M["by_chunk"]):
    t=k.split("_")[0]
    if t in done: continue
    fs=M["by_chunk"][k]
    rows.append("%s（%s–%s，%d 檔）"%(k,fs[0],fs[-1],len(fs)))
io.open(os.path.join(OUT,"_pending.txt"),"w",encoding="utf-8").write("\n".join(rows))
print(len(rows))
