import json, io
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
def show(gid, term, w=90):
    e = next(x for x in ents if x["gid"]==gid)
    cur = e["current"]
    i = cur.find(term)
    print("###", gid, "len", len(cur), "idx", i)
    if i>=0:
        print("CTX:", cur[max(0,i-w):i+len(term)+w])
    else:
        print("NO TERM; near:")
        print(cur[:600])
    print()
show("011-0006","古人")
show("040-0011","應當指給")
show("062-0120","有時")
show("065-0046","九月二十四日")
