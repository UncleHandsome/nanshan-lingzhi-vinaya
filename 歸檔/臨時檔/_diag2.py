import json, io
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
out=[]
def show(gid, term, w=110):
    e = next(x for x in ents if x["gid"]==gid)
    cur = e["current"]
    out.append("### %s len=%d" % (gid, len(cur)))
    i = cur.find(term)
    if i>=0:
        out.append(cur[max(0,i-w):i+len(term)+w])
    else:
        out.append("NO TERM "+term)
        out.append(cur[:700])
    out.append("")
show("011-0006","古人")
show("040-0011","應當指給")
show("062-0120","有時")
show("065-0046","九月二十四日")
io.open(OUT+"/diag2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
