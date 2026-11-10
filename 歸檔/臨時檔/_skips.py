import json, io
OUT = r"AI語譯/_work/review/_re0"
sk = json.load(io.open(OUT+"/skips.json", encoding="utf-8"))
out=[]
for gid,book,chunk,seg,reason in sk:
    out.append("%s\t%s#%d\t%s" % (gid, chunk, seg, reason))
io.open(OUT+"/skips.txt","w",encoding="utf-8").write("\n".join(out))
print(len(sk))
