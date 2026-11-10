import json, io, sys
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(OUT + "/uniq2.json", encoding="utf-8"))
for e in ents:
    if e["chunk"].startswith("04b") and e["seg"]==13:
        print(e["gid"], e["seg"], e["type"], "inD", e["gid"] in D)
        print("  pairs:", [p[:2] for p in e["pairs"]])
