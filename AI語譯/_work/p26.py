import json,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
p=json.load(open(r"AI語譯\_work\parsed2.json",encoding="utf-8"))
w={ (r["base"],r["src"]):r for r in json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8")) }
# 117 條 -> (loc, sug)
import re
def base(k): return re.sub(r'\s*[（(][^）)]*[）)]\s*$','',k).strip()
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
bk={b["key"]:b for b in blocks}
yes=[e for e in p if e["verdict"]=="是錯"]
g=collections.defaultdict(list)
for e in yes:
    b=base(e["key"]); loc=(bk[b]["book"],bk[b]["chunk"],bk[b]["para"]) if b in bk else ("?",)
    g[(loc,e["sug"])].append((e["src"],e["key"]))
dups={k:v for k,v in g.items() if len(v)>1}
print("groups with dup:",len(dups),"removed:",sum(len(v)-1 for v in dups.values()))
for k,v in dups.items():
    print(k[0], [x for x in v])
