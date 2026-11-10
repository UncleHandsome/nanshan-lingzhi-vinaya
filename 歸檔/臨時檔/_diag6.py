import json, io, sys
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
e = next(x for x in ents if x["gid"]=="011-0006")
out=[repr(e["type"]), repr(e["gid"]+"|"+e["type"])]
out += [repr(k) for k in D if k.startswith("011-0006")]
io.open(OUT+"/diag6.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
