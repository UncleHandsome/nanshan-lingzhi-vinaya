import json
from collections import defaultdict
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
g=defaultdict(set)
for x in d: g[(x["chunk"],x["seg"])].add(x["CUR"])
bad=[(k,len(v)) for k,v in g.items() if len(v)>1]
print("segments with differing current:", len(bad), bad[:5])
print("segments total", len(g))
# how many rows per segment
from collections import Counter
c=Counter((x["chunk"],x["seg"]) for x in d)
print("max rows per seg", max(c.values()), [k for k,v in c.items() if v==max(c.values())][:3])
