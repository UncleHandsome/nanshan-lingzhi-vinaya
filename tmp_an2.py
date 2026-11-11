import json,io,collections,os
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
R=json.load(io.open(os.path.join(ROOT,"AI語譯","_work","review","_r2_02","_refs.json"),encoding="utf-8"))
by=R["by_chunk"]
# invert: resp -> chunks
inv=collections.defaultdict(list)
for ch,pres in by.items():
    for p in pres:
        if 550<=int(p)<=641: inv[p].append(ch)
nums=sorted(int(x) for x in inv)
print("resp in refs:",len(nums))
missing=[n for n in range(550,642) if n not in nums]
print("missing from refs:",missing)
# chunk coverage
for ch in sorted(by, key=lambda s: s):
    ps=[p for p in by[ch] if 550<=int(p)<=641]
    if ps: print(ch, len(ps), sorted(ps,key=int))
