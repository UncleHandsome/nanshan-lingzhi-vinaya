# verify report current == book paragraph for a few segs
import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
def load(ch):
    p=rf"AI語譯\out\03_業疏\{ch}.txt"
    lines=open(p,encoding="utf-8").read().split("\n")
    return [l for l in lines if l.strip()]
import random
random.seed(1)
sample=random.sample(d,8)
for x in sample:
    ls=load(x["chunk"])
    # find line equal to CUR
    hit=[i for i,l in enumerate(ls) if l.strip()==x["CUR"].strip()]
    print(x["gid"],x["chunk"],x["seg"],"match_idx",hit[:3],"nlines",len(ls))
