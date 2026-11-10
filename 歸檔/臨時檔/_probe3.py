import json, io
d = json.load(io.open(r"AI語譯/_work/review/_re0/dups.json", encoding="utf-8"))
for x in d: print(x["gid"], x["seg"], x["type"])
