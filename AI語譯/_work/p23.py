import json,collections,sys
sys.stdout.reconfigure(encoding="utf-8")
p=json.load(open(r"AI語譯\_work\parsed2.json",encoding="utf-8"))
c=collections.Counter((e["src"],e["verdict"]) for e in p)
for k,v in sorted(c.items()): print(k,v)
print()
for e in p:
    if e["verdict"] not in ("是錯","不是錯"):
        print(e["src"], e["key"], e["verdict"], (e["judge"] or "")[:60])
