import sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\04_比丘尼鈔"
import collections
for fn in sorted(os.listdir(base)):
    if not fn.endswith(".txt"): continue
    txt=io.open(os.path.join(base,fn),encoding="utf-8").read().replace("\r\n","\n")
    bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
    d=collections.defaultdict(list)
    for i,b in enumerate(bl): d[b].append(i+1)
    dups={k:v for k,v in d.items() if len(v)>1}
    if dups:
        print(fn, "dup blocks:", [(v, k[:30]) for k,v in dups.items()])
print("done")
