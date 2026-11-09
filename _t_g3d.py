import sys, json
sys.stdout.reconfigure(encoding="utf-8")
rows=json.load(open("_g2rows.json",encoding="utf-8"))
used=set(json.load(open("_g2used.json",encoding="utf-8")))
SKIP={15,63,101,113,132,153,165,173,30,40,45,46,92,94,96,99,100,69,29,70}
dedup=set(i for i,r in enumerate(rows) if "重複貼上" in r[6])
nosug=set(i for i,r in enumerate(rows) if not r[7].strip())
print("total",len(rows),"used",len(used),"dedup",len(dedup),"nosug",len(nosug))
unacc=[i for i in range(len(rows)) if i not in used and i not in SKIP and i not in dedup and i not in nosug]
print("unaccounted:",unacc)
for i in unacc:
    r=rows[i]; print(i, r[2], r[3], r[5], "|", r[6][:80], "|", r[7][:80])
skip_auto = SKIP - {29,70}
print("applied rows:", len(used))
print("skipped rows:", len(rows)-len(used))
print("dedup rows skipped:", len(dedup - used))
print("nosug skipped:", len(nosug - used))
print("SKIP-set rows skipped:", len([x for x in skip_auto if x not in used]))
