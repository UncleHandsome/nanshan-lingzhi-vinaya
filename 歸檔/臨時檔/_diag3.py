import json, io, sys
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
e = next(x for x in ents if x["gid"]=="011-0006")
cur = e["current"]
old = D["011-0006"][1]
print("old len", len(old), "in cur:", old in cur)
i = cur.find("古人說")
seg = cur[i:i+len(old)]
print("cur seg:", seg)
print("old    :", old)
for j,(a,b) in enumerate(zip(seg, old)):
    if a!=b:
        print("diff at", j, repr(a), hex(ord(a)), repr(b), hex(ord(b)))
print("len seg", len(seg))
