import sys, json
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
from _rv_kit import parse_x7
m={}
for n in range(895,932):
    for s in parse_x7(str(n)):
        m[(s["chunk"],s["idx"])]=s["no"]
edits={"11a_卷三上之二":[8,12,15,18,30,31,34,36,48,49,51,89,22,72,76,91,97,107,117,120,140],
       "11b_卷三上之二":[41,58,2,29,52,102],
       "11c_卷三上之二":[56,107]}
tot=0
for ch,idxs in edits.items():
    nos=[m.get((ch,i),"??#%d"%i) for i in idxs]
    print(ch, len(idxs), " ".join(nos))
    tot+=len(idxs)
print("total edits(seg-count incl dup)",tot)
