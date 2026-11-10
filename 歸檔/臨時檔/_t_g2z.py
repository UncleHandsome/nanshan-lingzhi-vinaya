import io, sys, os, glob
sys.stdout.reconfigure(encoding="utf-8")
# find blocks with internal newline in candidate books
targets={"02_戒疏":[], "資持記":[], "03_業疏":[]}
for book in targets:
    d=os.path.join(r"AI語譯\out",book)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"): continue
        txt=io.open(os.path.join(d,fn),encoding="utf-8").read().replace("\r\n","\n")
        bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
        for i,b in enumerate(bl):
            if "\n" in b:
                targets[book].append((fn,i+1,b[:60]))
for k,v in targets.items():
    print(k, "blocks with newline:", len(v))
    for x in v[:5]: print("   ",x)
