import json, io, re
ents = json.load(io.open(r"AI語譯/_work/review/_re0/uniq2.json", encoding="utf-8"))
buckets = {}
for e in ents:
    k = e["pairs"][0][0]
    buckets.setdefault(k, []).append(e)
for k, v in buckets.items():
    print("=====", k, len(v))
# print first 4 'other' and first 4 'NEW-ONLY'
for k in ["other", "改為X"]:
    print("@@@@@@@@", k)
    for e in buckets[k][:4]:
        print("---", e["gid"], e["seg"], e["type"])
        print("CUR:", e["current"][:300])
        print("PROB:", e["problem"][:300])
        print("SUG:", e["suggestion"][:300])
