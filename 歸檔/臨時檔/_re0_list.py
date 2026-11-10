import json, io
ents = json.load(io.open(r"AI語譯/_work/review/_re0/uniq2.json", encoding="utf-8"))
import re
Q = re.compile(r"「([^「」]*)」")
for e in sorted(ents, key=lambda x:(x["book"],x["chunk"],x["seg"],x["gid"])):
    pairs=e["pairs"]; kind=pairs[0][0]; cur=e["current"] or ""
    if kind in ("將A改為B","A改為B"):
        c="CLEAN" if any((p[1] or "").strip() and p[1] in cur for p in pairs) else "OLDMISS"
    elif kind=="刪除":
        c="CLEAN" if (pairs[0][1] and pairs[0][1] in cur) else "OLDMISS"
    elif kind=="改為X": c="NEWONLY"
    else: c="OTHER"
    if c!="CLEAN":
        print("%s\t%d\t%s\t%s" % (e["gid"], e["seg"], c, e["type"]))
