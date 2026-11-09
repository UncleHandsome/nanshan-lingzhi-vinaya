import sys, json
sys.stdout.reconfigure(encoding="utf-8")
keep=json.load(open("_g2keep.json",encoding="utf-8"))
from collections import OrderedDict
ch=OrderedDict()
for i,r in keep:
    ch.setdefault(r[2], OrderedDict()).setdefault(r[3], r)
for k,v in ch.items():
    print(k, "segs", len(v), "chars", sum(len(x[9]) for x in v.values()))
