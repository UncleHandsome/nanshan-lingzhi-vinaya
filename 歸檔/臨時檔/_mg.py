import json, io
OUT = r"AI語譯/_work/review/_re0"
rows = json.load(io.open(OUT+"/rows.json", encoding="utf-8"))
want = [("02_戒疏","02b_卷一上之二",123),("01_行事鈔","03b_卷上之三",21),("02_戒疏","04c_卷一上之二",106),("02_戒疏","09a_卷二下之二",70),("01_行事鈔","04b_卷上之四",13)]
out=[]
for r in rows:
    if (r["book"],r["chunk"],r["seg"]) in want:
        out.append("### %s %s#%d" % (r["book"],r["chunk"],r["seg"]))
        out.append("NEW: "+r["new"])
        out.append("")
io.open(OUT+"/merged.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
