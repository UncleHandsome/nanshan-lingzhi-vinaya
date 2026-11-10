import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
used=set(json.load(open("_g2used.json",encoding="utf-8")))
for i,r in enumerate(rows):
    if "重複" in r[6] and "重複貼上" not in r[6]:
        print(i, r[2], r[3], r[5], "used" if i in used else "NOT-USED")
        print("  P:", r[6])
        print("  S:", r[7])
