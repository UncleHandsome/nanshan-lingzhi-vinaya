import json,sys,os,collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
print("rows",len(w))
c=collections.Counter((r["base"],r["book"],r["chunk"],r["found"]) for r in w)
for k,v in c.items():
    if v>1: print("dup-loc",k,v)
p=json.load(open(r"AI語譯\_work\parsed2.json",encoding="utf-8"))
yes=[e for e in p if e["verdict"]=="是錯"]
print("total yes",len(yes))
seen=set()
for e in yes:
    k=(e["key"],e["sug"])
print("distinct sug per key:", sum(1 for _ in {(e["key"],e["sug"]) for e in yes}))
